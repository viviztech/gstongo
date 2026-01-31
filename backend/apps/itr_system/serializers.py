"""
Serializers for ITR Filing.
"""
from rest_framework import serializers
from .models import ITRFiling, ITR1Details, ITRDocument


class ITR1DetailsSerializer(serializers.ModelSerializer):
    """Serializer for ITR-1 details."""
    
    class Meta:
        model = ITR1Details
        fields = [
            'salary_income', 'house_property_income', 'other_sources_income',
            'deduction_80c', 'deduction_80d', 'other_deductions',
            'tax_payable', 'rebate_87a', 'surcharge', 'health_education_cess',
            'form_data', 'created_at', 'updated_at'
        ]


class ITRDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ITR documents."""
    
    class Meta:
        model = ITRDocument
        fields = ['id', 'document_type', 'file', 'uploaded_at']


class ITRFilingSerializer(serializers.ModelSerializer):
    """Serializer for ITRFiling model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    itr1_details = ITR1DetailsSerializer(read_only=True)
    documents = ITRDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ITRFiling
        fields = [
            'id', 'user', 'user_email', 'filing_type', 'financial_year',
            'assessment_year', 'status', 'total_income', 'total_tax_liability',
            'total_tax_paid', 'tax_due', 'refund_amount',
            'acknowledgment_number', 'filed_at', 'itr1_details', 'documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'acknowledgment_number',
            'filed_at', 'created_at', 'updated_at'
        ]


class ITRFilingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ITR filing."""
    
    class Meta:
        model = ITRFiling
        fields = ['filing_type', 'financial_year', 'assessment_year']
    
    def validate(self, attrs):
        """Check for duplicate filing."""
        user = self.context['request'].user
        attrs['user'] = user
        
        # Check if filing already exists
        existing = ITRFiling.objects.filter(
            user=user,
            filing_type=attrs['filing_type'],
            financial_year=attrs['financial_year']
        ).exists()
        
        if existing:
            raise serializers.ValidationError({
                'filing': 'An ITR filing of this type for the same period already exists.'
            })
        
        return attrs
