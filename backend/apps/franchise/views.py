"""
Views for Franchise Management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Franchise, FranchiseTerritory, FranchiseCommission, PincodeMapping, CustomerAssignment
from .serializers import (
    FranchiseSerializer, FranchiseCreateSerializer, FranchiseTerritorySerializer,
    FranchiseCommissionSerializer, PincodeMappingSerializer, CustomerAssignmentSerializer
)


class FranchiseViewSet(viewsets.ModelViewSet):
    serializer_class = FranchiseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Franchise.objects.all()
        return Franchise.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FranchiseCreateSerializer
        return FranchiseSerializer
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        franchise = self.get_object()
        
        # Get stats
        stats = {
            'total_customers': franchise.total_customers,
            'total_revenue': float(franchise.total_revenue),
            'rating': float(franchise.rating),
            'territories_count': franchise.territories.filter(is_active=True).count(),
            'pending_commissions': franchise.commissions.filter(status='pending').aggregate(
                total=Sum('net_payable')
            )['total'] or 0,
        }
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def commissions(self, request, pk=None):
        franchise = self.get_object()
        commissions = franchise.commissions.all().order_by('-year', '-month')
        serializer = FranchiseCommissionSerializer(commissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def customers(self, request, pk=None):
        franchise = self.get_object()
        assignments = franchise.assigned_customers.filter(is_active=True)
        serializer = CustomerAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class PincodeMappingViewSet(viewsets.ModelViewSet):
    queryset = PincodeMapping.objects.all()
    serializer_class = PincodeMappingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PincodeMapping.objects.all()
        state = self.request.query_params.get('state')
        district = self.request.query_params.get('district')
        if state:
            queryset = queryset.filter(state__icontains=state)
        if district:
            queryset = queryset.filter(district__icontains=district)
        return queryset
    
    @action(detail=False, methods=['get'])
    def lookup(self, request):
        pincode = request.query_params.get('pincode')
        if not pincode:
            return Response({'error': 'Pincode is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mapping = PincodeMapping.objects.get(pincode=pincode, is_active=True)
            serializer = self.get_serializer(mapping)
            return Response(serializer.data)
        except PincodeMapping.DoesNotExist:
            return Response({'error': 'Pincode not found'}, status=status.HTTP_404_NOT_FOUND)


class CustomerAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomerAssignment.objects.all()
        if hasattr(user, 'franchise'):
            return CustomerAssignment.objects.filter(franchise=user.franchise)
        return CustomerAssignment.objects.filter(customer=user)
