"""
Views for ITR Filing module.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ITRFiling, ITR1Details, ITRDocument
from .serializers import (
    ITRFilingSerializer, ITRFilingCreateSerializer,
    ITR1DetailsSerializer, ITRDocumentSerializer
)


class ITRFilingViewSet(viewsets.ModelViewSet):
    """ViewSet for ITR Filing operations."""
    
    serializer_class = ITRFilingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter filings by user."""
        return ITRFiling.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ITRFilingCreateSerializer
        return ITRFilingSerializer
    
    def perform_create(self, serializer):
        """Automatically set the user and create initial details."""
        filing = serializer.save(user=self.request.user)
        
        # Create initial details based on type
        if filing.filing_type == 'ITR1':
            ITR1Details.objects.create(filing=filing)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload a document for ITR filing."""
        filing = self.get_object()
        serializer = ITRDocumentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(filing=filing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_details(self, request, pk=None):
        """Update ITR specific details."""
        filing = self.get_object()
        
        if filing.filing_type == 'ITR1':
            details = filing.itr1_details
            serializer = ITR1DetailsSerializer(details, data=request.data, partial=True)
        else:
            return Response(
                {'error': f'Details update not implemented for {filing.filing_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
