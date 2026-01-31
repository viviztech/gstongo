"""
Views for Business Services module.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    ServiceApplication, ServiceDocument, CompanyIncorporation,
    FSSAIRegistration, MSMERegistration, PANTANApplication
)
from .serializers import (
    ServiceApplicationSerializer, ServiceApplicationCreateSerializer,
    ServiceDocumentSerializer, CompanyIncorporationSerializer,
    FSSAIRegistrationSerializer, MSMERegistrationSerializer, PANTANApplicationSerializer
)


class ServiceApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ServiceApplication.objects.filter(user=self.request.user)
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceApplicationCreateSerializer
        return ServiceApplicationSerializer
    
    def perform_create(self, serializer):
        application = serializer.save()
        
        # Create service-specific details based on type
        service_type = application.service_type
        if service_type == 'company_incorporation':
            CompanyIncorporation.objects.create(
                application=application,
                proposed_name_1='',
                company_type='pvt_ltd',
                authorized_capital=0,
                paid_up_capital=0,
                registered_address='',
                business_activity=''
            )
        elif service_type == 'fssai_registration':
            FSSAIRegistration.objects.create(
                application=application,
                license_type='basic',
                business_name='',
                food_category='',
                premise_address='',
                contact_person='',
                contact_phone='',
                annual_turnover=0
            )
        elif service_type == 'msme_registration':
            MSMERegistration.objects.create(
                application=application,
                enterprise_name='',
                enterprise_type='micro',
                nic_code='',
                major_activity='',
                plant_address='',
                investment_in_plant=0,
                annual_turnover=0
            )
        elif service_type in ['pan_application', 'tan_application']:
            PANTANApplication.objects.create(
                application=application,
                application_type='pan_new' if service_type == 'pan_application' else 'tan_new',
                applicant_name='',
                address='',
                email='',
                phone=''
            )
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        application = self.get_object()
        serializer = ServiceDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(application=application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        application = self.get_object()
        if application.status == 'draft':
            application.status = 'documents_pending'
            application.submitted_at = timezone.now()
            application.save()
            return Response({'status': 'Application submitted successfully'})
        return Response({'error': 'Application already submitted'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_details(self, request, pk=None):
        application = self.get_object()
        service_type = application.service_type
        
        if service_type == 'company_incorporation' and hasattr(application, 'company_details'):
            serializer = CompanyIncorporationSerializer(application.company_details, data=request.data, partial=True)
        elif service_type == 'fssai_registration' and hasattr(application, 'fssai_details'):
            serializer = FSSAIRegistrationSerializer(application.fssai_details, data=request.data, partial=True)
        elif service_type == 'msme_registration' and hasattr(application, 'msme_details'):
            serializer = MSMERegistrationSerializer(application.msme_details, data=request.data, partial=True)
        elif service_type in ['pan_application', 'tan_application'] and hasattr(application, 'pantan_details'):
            serializer = PANTANApplicationSerializer(application.pantan_details, data=request.data, partial=True)
        else:
            return Response({'error': 'Details not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
