"""
Views for Analytics and Reporting.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from .models import (
    ReportTemplate, GeneratedReport, ScheduledReport,
    DashboardWidget, UserDashboard, AuditLog, APIKey, Webhook
)
from .serializers import (
    ReportTemplateSerializer, GeneratedReportSerializer, ScheduledReportSerializer,
    DashboardWidgetSerializer, UserDashboardSerializer, AuditLogSerializer,
    APIKeySerializer, APIKeyCreateSerializer, WebhookSerializer, WebhookCreateSerializer
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ReportTemplate.objects.all()
        return ReportTemplate.objects.filter(created_by=user) | ReportTemplate.objects.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GeneratedReportViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GeneratedReport.objects.filter(requested_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        report = self.get_object()
        report.status = 'pending'
        report.save()
        # In production, trigger async task here
        return Response({'status': 'Report regeneration queued'})


class ScheduledReportViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ScheduledReport.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response({'is_active': schedule.is_active})


class DashboardViewSet(viewsets.ViewSet):
    """Aggregated analytics dashboard data."""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall platform summary."""
        from apps.gst_filing.models import GSTFiling
        from apps.itr_system.models import ITRFiling
        from apps.support.models import SupportTicket, JobTicket
        from apps.document_vault.models import OrderTracking
        
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # GST Filings stats
        gst_stats = GSTFiling.objects.filter(user=user).aggregate(
            total=Count('id'),
            filed=Count('id', filter=models.Q(status='filed')),
            pending=Count('id', filter=models.Q(status__in=['draft', 'pending', 'in_progress']))
        )
        
        # ITR stats
        itr_stats = ITRFiling.objects.filter(user=user).aggregate(
            total=Count('id'),
            filed=Count('id', filter=models.Q(status='filed')),
        )
        
        # Support tickets
        ticket_stats = SupportTicket.objects.filter(customer=user).aggregate(
            total=Count('id'),
            open=Count('id', filter=models.Q(status__in=['open', 'in_progress'])),
        )
        
        return Response({
            'gst_filings': gst_stats,
            'itr_filings': itr_stats,
            'support_tickets': ticket_stats,
            'summary_date': today,
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get filing trends over time."""
        from apps.gst_filing.models import GSTFiling
        
        six_months_ago = timezone.now() - timedelta(days=180)
        
        monthly_filings = GSTFiling.objects.filter(
            user=request.user,
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'monthly_filings': list(monthly_filings)
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = AuditLog.objects.all()
        user_id = self.request.query_params.get('user')
        action = self.request.query_params.get('action')
        resource_type = self.request.query_params.get('resource_type')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        return queryset


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Return full key only on creation
        return Response({
            'id': str(instance.id),
            'name': instance.name,
            'key': instance._full_key,  # Full key only shown once
            'message': 'Save this key securely. It will not be shown again.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({'status': 'API key revoked'})


class WebhookViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WebhookCreateSerializer
        return WebhookSerializer
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        webhook = self.get_object()
        # In production, send test webhook
        return Response({'status': 'Test webhook sent', 'url': webhook.url})
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        webhook = self.get_object()
        webhook.is_active = not webhook.is_active
        webhook.save()
        return Response({'is_active': webhook.is_active})
