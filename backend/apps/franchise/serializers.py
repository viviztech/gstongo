"""
Serializers for Franchise Management.
"""
from rest_framework import serializers
from .models import Franchise, FranchiseTerritory, FranchiseCommission, PincodeMapping, CustomerAssignment


class FranchiseTerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FranchiseTerritory
        fields = ['id', 'state', 'district', 'pincode_start', 'pincode_end', 'is_exclusive', 'is_active']


class FranchiseCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FranchiseCommission
        fields = [
            'id', 'month', 'year', 'gross_revenue', 'commission_rate', 
            'commission_amount', 'deductions', 'net_payable', 'status', 
            'paid_at', 'payment_reference', 'created_at'
        ]


class FranchiseSerializer(serializers.ModelSerializer):
    territories = FranchiseTerritorySerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Franchise
        fields = [
            'id', 'user', 'user_email', 'franchise_code', 'business_name', 'franchise_type',
            'contact_person', 'contact_phone', 'contact_email',
            'address', 'city', 'state', 'pincode',
            'pan_number', 'gst_number', 'kyc_verified',
            'agreement_signed', 'agreement_date', 'agreement_expiry',
            'security_deposit', 'commission_rate', 'status',
            'total_customers', 'total_revenue', 'rating',
            'territories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'franchise_code', 'kyc_verified', 'total_customers', 'total_revenue', 'rating']


class FranchiseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = [
            'business_name', 'franchise_type', 'contact_person', 'contact_phone', 'contact_email',
            'address', 'city', 'state', 'pincode', 'pan_number', 'gst_number',
            'bank_account_number', 'bank_ifsc'
        ]
    
    def create(self, validated_data):
        import uuid
        validated_data['user'] = self.context['request'].user
        validated_data['franchise_code'] = f"FR{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class PincodeMappingSerializer(serializers.ModelSerializer):
    franchise_name = serializers.CharField(source='franchise.business_name', read_only=True)
    
    class Meta:
        model = PincodeMapping
        fields = ['id', 'pincode', 'franchise', 'franchise_name', 'state', 'district', 'region', 'is_active', 'priority']


class CustomerAssignmentSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    franchise_name = serializers.CharField(source='franchise.business_name', read_only=True)
    
    class Meta:
        model = CustomerAssignment
        fields = ['id', 'customer', 'customer_email', 'franchise', 'franchise_name', 'assigned_by', 'assigned_at', 'is_active', 'notes']
