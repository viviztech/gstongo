"""
Views for Document Vault.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import uuid
import os
from .models import Document, DocumentCategory, DocumentShare, OrderTracking
from .serializers import (
    DocumentSerializer, DocumentCategorySerializer,
    DocumentShareSerializer, OrderTrackingSerializer
)


class DocumentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Document.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')
        if category:
            queryset = queryset.filter(category_id=category)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        file_type = ''
        file_size = 0
        if file:
            file_type = os.path.splitext(file.name)[1].lower()
            file_size = file.size
        serializer.save(
            user=self.request.user,
            file_type=file_type,
            file_size=file_size
        )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        document = self.get_object()
        expires_hours = request.data.get('expires_hours', 24)
        shared_with_email = request.data.get('email')
        
        share = DocumentShare.objects.create(
            document=document,
            share_token=uuid.uuid4().hex,
            shared_with_email=shared_with_email,
            expires_at=timezone.now() + timezone.timedelta(hours=expires_hours)
        )
        
        serializer = DocumentShareSerializer(share)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        document = self.get_object()
        document.status = 'archived'
        document.save()
        return Response({'status': 'Document archived'})


class OrderTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OrderTracking.objects.filter(user=self.request.user)
