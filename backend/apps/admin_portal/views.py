"""
Views for Admin Portal.
"""
import uuid
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import (
    AdminDashboardStats, UserSearchHistory, AdminActivityLog,
    SystemSettings, PincodeMapping
)
from .serializers import (
    DashboardStatsSerializer, DashboardSummarySerializer,
    UserSearchSerializer, UserSearchResultSerializer,
    AdminActivityLogSerializer, SystemSettingsSerializer,
    PincodeMappingSerializer, FilingReportSerializer, PaymentReportSerializer
)

User = get_user_model()


class AdminAccessMixin:
    """Mixin to check admin access."""
    
    def has_admin_access(self):
        """Check if user has admin access."""
        if not hasattr(self.request.user, 'admin_profile'):
            return False
        return True
    
    def check_permission(self, permission):
        """Check specific admin permission."""
        if not hasattr(self.request.user, 'admin_profile'):
            return False
        profile = self.request.user.admin_profile
        return getattr(profile, permission, False)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for admin dashboard."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get dashboard summary."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # User stats
        total_users = User.objects.filter(is_active=True).count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        new_users_this_week = User.objects.filter(date_joined__date__gte=week_start).count()
        new_users_this_month = User.objects.filter(date_joined__date__gte=month_start).count()
        
        # Filing stats
        from apps.gst_filing.models import GSTFiling
        total_filings = GSTFiling.objects.count()
        pending_filings = GSTFiling.objects.filter(status='pending').count()
        filed_today = GSTFiling.objects.filter(status='filed', filed_at__date=today).count()
        nil_filings_count = GSTFiling.objects.filter(nil_filing=True).count()
        
        # Payment stats
        from apps.invoices.models import Invoice, PaymentRecord
        total_collected = PaymentRecord.objects.filter(
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending_invoices = Invoice.objects.filter(status='issued')
        pending_amount = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        overdue_invoices = Invoice.objects.filter(status='overdue')
        overdue_count = overdue_invoices.count()
        overdue_amount = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'total_users': total_users,
            'new_users_today': new_users_today,
            'new_users_this_week': new_users_this_week,
            'new_users_this_month': new_users_this_month,
            'total_filings': total_filings,
            'pending_filings': pending_filings,
            'filed_today': filed_today,
            'nil_filings_count': nil_filings_count,
            'total_collected': total_collected,
            'pending_amount': pending_amount,
            'overdue_count': overdue_count,
            'overdue_amount': overdue_amount,
        })
    
    @action(detail=False, methods=['get'])
    def filing_report(self, request):
        """Get filing report by type."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.gst_filing.models import GSTFiling
        
        report = []
        for filing_type, _ in GSTFiling.FILING_TYPES:
            filings = GSTFiling.objects.filter(filing_type=filing_type)
            report.append({
                'filing_type': filing_type,
                'total_count': filings.count(),
                'filed_count': filings.filter(status='filed').count(),
                'pending_count': filings.filter(status='pending').count(),
                'nil_count': filings.filter(nil_filing=True).count(),
                'total_taxable_value': sum(f.total_taxable_value for f in filings),
                'total_tax': sum(f.total_tax for f in filings),
            })
        
        return Response(report)
    
    @action(detail=False, methods=['get'])
    def payment_report(self, request):
        """Get payment collection report."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.invoices.models import Invoice, PaymentRecord
        
        total_invoiced = Invoice.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        total_collected = PaymentRecord.objects.filter(
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending_invoices = Invoice.objects.filter(status='issued')
        pending_amount = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        overdue_invoices = Invoice.objects.filter(status='overdue')
        overdue_amount = overdue_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        collection_rate = (total_collected / total_invoiced * 100) if total_invoiced > 0 else 0
        
        return Response({
            'total_invoiced': total_invoiced,
            'total_collected': total_collected,
            'pending_amount': pending_amount,
            'overdue_amount': overdue_amount,
            'collection_rate': round(collection_rate, 2),
        })


class UserSearchViewSet(viewsets.ViewSet):
    """ViewSet for user search operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get search history."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_manage_users:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        history = UserSearchHistory.objects.filter(
            admin=request.user
        ).order_by('-searched_at')[:50]
        
        return Response(history.values())
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search for users by CIN, GST, name, etc."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_manage_users:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        search_type = serializer.validated_data['search_type']
        search_value = serializer.validated_data['search_value']
        
        # Perform search
        queryset = User.objects.filter(is_active=True)
        
        if search_type == 'cin':
            queryset = queryset.filter(profile__cin__icontains=search_value)
        elif search_type == 'gst':
            queryset = queryset.filter(profile__gst_number__icontains=search_value)
        elif search_type == 'name':
            queryset = queryset.filter(
                Q(first_name__icontains=search_value) |
                Q(last_name__icontains=search_value)
            )
        elif search_type == 'email':
            queryset = queryset.filter(email__icontains=search_value)
        elif search_type == 'phone':
            queryset = queryset.filter(phone_number__icontains=search_value)
        elif search_type == 'pincode':
            queryset = queryset.filter(profile__pincode=search_value)
        
        # Log search
        UserSearchHistory.objects.create(
            admin=request.user,
            search_type=search_type,
            search_value=search_value,
            result_count=queryset.count()
        )
        
        results = []
        for user in queryset[:100]:  # Limit to 100 results
            results.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'cin': user.profile.cin if hasattr(user, 'profile') else None,
                'gst_number': user.profile.gst_number if hasattr(user, 'profile') else None,
                'pincode': user.profile.pincode if hasattr(user, 'profile') else None,
                'created_at': user.date_joined,
                'is_active': user.is_active,
            })
        
        return Response({
            'search_type': search_type,
            'search_value': search_value,
            'result_count': len(results),
            'results': results
        })


class AdminActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for admin activity logs."""
    
    serializer_class = AdminActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_view_reports:
            return AdminActivityLog.objects.none()
        
        queryset = AdminActivityLog.objects.all()
        
        # Filter by admin
        admin_id = self.request.query_params.get('admin_id')
        if admin_id:
            queryset = queryset.filter(admin_id=admin_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def log(self, request):
        """Log an admin activity."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activity = AdminActivityLog.objects.create(
            admin=request.user,
            action=request.data.get('action'),
            target_type=request.data.get('target_type'),
            target_id=request.data.get('target_id'),
            description=request.data.get('description'),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        return Response({
            'message': 'Activity logged.',
            'activity_id': activity.id
        })
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for system settings."""
    
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_manage_admins:
            return SystemSettings.objects.none()
        return SystemSettings.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create system setting."""
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_manage_admins:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update system setting."""
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_manage_admins:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class PincodeMappingViewSet(viewsets.ModelViewSet):
    """ViewSet for pincode mapping management."""
    
    serializer_class = PincodeMappingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return PincodeMapping.objects.none()
        return PincodeMapping.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create pincode mapping."""
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_manage_users:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload pincode mappings."""
        if not hasattr(self.request.user, 'admin_profile') or not self.request.user.admin_profile.can_manage_users:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # This would handle bulk CSV upload
        return Response({'message': 'Bulk upload endpoint ready.'})
    
    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """Get pincodes grouped by region."""
        if not hasattr(self.request.user, 'admin_profile'):
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        regions = {}
        for mapping in PincodeMapping.objects.filter(is_active=True):
            if mapping.region_name not in regions:
                regions[mapping.region_name] = []
            regions[mapping.region_name].append({
                'pincode': mapping.pincode,
                'state': mapping.state,
                'district': mapping.district,
            })
        
        return Response(regions)
