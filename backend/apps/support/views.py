"""
Views for Support & Ticketing.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Enquiry, SupportTicket, TicketComment, JobTicket, JobTask, KnowledgeBase
from .serializers import (
    EnquirySerializer, EnquiryCreateSerializer,
    SupportTicketSerializer, SupportTicketCreateSerializer, TicketCommentSerializer,
    JobTicketSerializer, JobTaskSerializer, KnowledgeBaseSerializer
)


class EnquiryViewSet(viewsets.ModelViewSet):
    """Public enquiries - create is public, others require auth."""
    queryset = Enquiry.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EnquiryCreateSerializer
        return EnquirySerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(customer=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SupportTicketCreateSerializer
        return SupportTicketSerializer
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Only staff can resolve tickets'}, status=status.HTTP_403_FORBIDDEN)
        
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.resolution_notes = request.data.get('notes', '')
        ticket.save()
        return Response({'status': 'Ticket resolved'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        ticket = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.rating = int(rating)
        ticket.feedback = feedback
        ticket.save()
        return Response({'status': 'Rating submitted'})


class JobTicketViewSet(viewsets.ModelViewSet):
    serializer_class = JobTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = JobTicket.objects.all()
        else:
            queryset = JobTicket.objects.filter(customer=user)
        
        status_filter = self.request.query_params.get('status')
        job_type = self.request.query_params.get('job_type')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        job = self.get_object()
        serializer = JobTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        job = self.get_object()
        if job.status == 'created' or job.status == 'assigned':
            job.status = 'in_progress'
            job.started_at = timezone.now()
            job.save()
            return Response({'status': 'Job started'})
        return Response({'error': 'Job cannot be started'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        job = self.get_object()
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        return Response({'status': 'Job completed'})


class KnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = KnowledgeBase.objects.filter(is_published=True)
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(content__icontains=search)
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        article = self.get_object()
        article.helpful_votes += 1
        article.save()
        return Response({'status': 'Vote recorded'})
