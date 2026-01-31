"""
Serializers for Business Services.
"""
from rest_framework import serializers
from .models import (
    ServiceApplication, ServiceDocument, CompanyIncorporation,
    FSSAIRegistration, MSMERegistration, PANTANApplication
)
import uuid


class ServiceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDocument
        fields = ['id', 'document_type', 'document_name', 'file', 'uploaded_at']


class CompanyIncorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyIncorporation
        exclude = ['application']


class FSSAIRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSSAIRegistration
        exclude = ['application']


class MSMERegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MSMERegistration
        exclude = ['application']


class PANTANApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PANTANApplication
        exclude = ['application']


class ServiceApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    documents = ServiceDocumentSerializer(many=True, read_only=True)
    company_details = CompanyIncorporationSerializer(read_only=True)
    fssai_details = FSSAIRegistrationSerializer(read_only=True)
    msme_details = MSMERegistrationSerializer(read_only=True)
    pantan_details = PANTANApplicationSerializer(read_only=True)
    
    class Meta:
        model = ServiceApplication
        fields = [
            'id', 'user', 'user_email', 'service_type', 'status', 'application_data',
            'application_reference', 'certificate_number', 'submitted_at', 'completed_at',
            'documents', 'company_details', 'fssai_details', 'msme_details', 'pantan_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'application_reference', 'certificate_number', 'submitted_at', 'completed_at']


class ServiceApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceApplication
        fields = ['service_type', 'application_data']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['application_reference'] = f"GST{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)
