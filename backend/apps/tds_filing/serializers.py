"""
Serializers for TDS Filing.
"""
from rest_framework import serializers
from .models import TDSReturn, TDSDeductee, TDSChallan


class TDSDeducteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDSDeductee
        fields = ['id', 'pan', 'name', 'section_code', 'date_of_payment', 
                  'amount_paid', 'tds_deducted', 'tds_deposited', 'challan_number', 'created_at']


class TDSChallanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDSChallan
        fields = ['id', 'challan_number', 'bsr_code', 'challan_date', 'amount', 'challan_type', 'created_at']


class TDSReturnSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    deductees = TDSDeducteeSerializer(many=True, read_only=True)
    challans = TDSChallanSerializer(many=True, read_only=True)
    
    class Meta:
        model = TDSReturn
        fields = [
            'id', 'user', 'user_email', 'return_type', 'financial_year', 'quarter',
            'status', 'tan_number', 'deductor_name', 'total_deducted', 'total_deposited',
            'acknowledgment_number', 'filed_at', 'deductees', 'challans',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'acknowledgment_number', 'filed_at', 'created_at', 'updated_at']


class TDSReturnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDSReturn
        fields = ['return_type', 'financial_year', 'quarter', 'tan_number', 'deductor_name']
    
    def validate(self, attrs):
        user = self.context['request'].user
        attrs['user'] = user
        existing = TDSReturn.objects.filter(
            user=user, return_type=attrs['return_type'],
            financial_year=attrs['financial_year'], quarter=attrs['quarter']
        ).exists()
        if existing:
            raise serializers.ValidationError({'filing': 'A TDS return for this period already exists.'})
        return attrs
