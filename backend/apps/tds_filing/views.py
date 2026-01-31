"""
Views for TDS Filing module.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TDSReturn, TDSDeductee, TDSChallan
from .serializers import (
    TDSReturnSerializer, TDSReturnCreateSerializer,
    TDSDeducteeSerializer, TDSChallanSerializer
)


class TDSReturnViewSet(viewsets.ModelViewSet):
    serializer_class = TDSReturnSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TDSReturn.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TDSReturnCreateSerializer
        return TDSReturnSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_deductee(self, request, pk=None):
        tds_return = self.get_object()
        serializer = TDSDeducteeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tds_return=tds_return)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_challan(self, request, pk=None):
        tds_return = self.get_object()
        serializer = TDSChallanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tds_return=tds_return)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
