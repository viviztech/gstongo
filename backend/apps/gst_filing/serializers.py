"""
Serializers for GST Filing.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import GSTFiling, GSTR1Details, GSTR3BDetails, GSTR9BDetails, Invoice, FilingDocument


class GSTFilingSerializer(serializers.ModelSerializer):
    """Serializer for GSTFiling model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_cin = serializers.CharField(source='user.profile.cin', read_only=True)
    
    class Meta:
        model = GSTFiling
        fields = [
            'id', 'user', 'user_email', 'user_cin', 'filing_type',
            'financial_year', 'month', 'year', 'status', 'nil_filing',
            'total_taxable_value', 'total_tax', 'declaration_statement',
            'declaration_signed', 'declaration_signed_at', 'filing_reference_number',
            'filed_at', 'filing_locked', 'lock_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'user_cin', 'filing_reference_number',
            'filed_at', 'created_at', 'updated_at'
        ]


class GSTFilingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating GST filing."""
    
    class Meta:
        model = GSTFiling
        fields = ['filing_type', 'financial_year', 'month', 'year', 'nil_filing']
    
    def validate(self, attrs):
        """Check for duplicate filing."""
        user = self.context['request'].user
        attrs['user'] = user
        
        # Check if filing already exists
        existing = GSTFiling.objects.filter(
            user=user,
            filing_type=attrs['filing_type'],
            financial_year=attrs['financial_year'],
            month=attrs['month']
        ).exists()
        
        if existing:
            raise serializers.ValidationError({
                'filing': 'A filing of this type for the same period already exists.'
            })
        
        return attrs


class GSTFilingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating GST filing."""
    
    class Meta:
        model = GSTFiling
        fields = ['status', 'nil_filing', 'total_taxable_value', 'total_tax']


class GSTR1DetailsSerializer(serializers.ModelSerializer):
    """Serializer for GSTR-1 details."""
    
    class Meta:
        model = GSTR1Details
        fields = [
            'b2b_invoices_count', 'b2b_invoices_value', 'b2b_invoices_tax',
            'b2c_invoices_count', 'b2c_invoices_value', 'b2c_invoices_tax',
            'export_invoices_count', 'export_value',
            'nil_rated_invoices_count', 'nil_rated_value',
            'debit_notes_count', 'credit_notes_count', 'net_notes_value',
            'invoice_data', 'created_at', 'updated_at'
        ]


class GSTR3BDetailsSerializer(serializers.ModelSerializer):
    """Serializer for GSTR-3B details."""
    
    class Meta:
        model = GSTR3BDetails
        fields = [
            'outward_taxable_supplies', 'outward_tax_amount',
            'inward_supplies', 'itc_reversal',
            'igst_credit', 'cgst_credit', 'sgst_credit', 'total_credit',
            'igst_liability', 'cgst_liability', 'sgst_liability', 'cess_liability',
            'interest_payable', 'late_fee_payable', 'tax_data',
            'created_at', 'updated_at'
        ]


class GSTR9BDetailsSerializer(serializers.ModelSerializer):
    """Serializer for GSTR-9B details."""
    
    class Meta:
        model = GSTR9BDetails
        fields = [
            'total_outward_supplies', 'total_inward_supplies',
            'total_tax_collected', 'total_tax_deposited',
            'total_itc_claimed', 'itc_reversed', 'net_itc',
            'annual_data', 'auditor_name', 'auditor_membership_number',
            'created_at', 'updated_at'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'invoice_type',
            'counterparty_gstin', 'counterparty_name',
            'taxable_value', 'igst', 'cgst', 'sgst', 'cess', 'total_tax',
            'hsn_code', 'export_port', 'shipping_bill_number', 'shipping_bill_date',
            'original_invoice_number', 'original_invoice_date', 'note_reason',
            'created_at'
        ]


class InvoiceUploadSerializer(serializers.Serializer):
    """Serializer for invoice Excel upload."""
    
    filing_id = serializers.UUIDField(required=True)
    file = serializers.FileField(required=True)
    
    def validate_file(self, value):
        """Validate file type."""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError('Only Excel files are allowed.')
        return value


class DeclarationSerializer(serializers.Serializer):
    """Serializer for filing declaration."""
    
    declaration_statement = serializers.CharField(required=True)
    declaration_signed = serializers.BooleanField(required=True)
    
    def validate_declaration_signed(self, value):
        if not value:
            raise serializers.ValidationError(
                'You must accept the declaration to file the return.'
            )
        return value


class FilingStatusSerializer(serializers.Serializer):
    """Serializer for updating filing status."""
    
    status = serializers.ChoiceField(
        choices=['draft', 'pending', 'in_progress', 'filed', 'rejected']
    )
    filing_reference_number = serializers.CharField(required=False)
    remarks = serializers.CharField(required=False)


class NilFilingSerializer(serializers.Serializer):
    """Serializer for nil filing."""
    
    declaration_statement = serializers.CharField(required=True)


class FilingSummarySerializer(serializers.Serializer):
    """Serializer for filing summary."""
    
    filing_type = serializers.CharField()
    financial_year = serializers.CharField()
    month = serializers.IntegerField()
    status = serializers.CharField()
    total_taxable_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
