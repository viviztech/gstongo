"""
Serializers for Invoices.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import RateSlab, ProformaInvoice, Invoice, PaymentRecord


class RateSlabSerializer(serializers.ModelSerializer):
    """Serializer for RateSlab model."""
    
    class Meta:
        model = RateSlab
        fields = [
            'id', 'name', 'min_invoices', 'max_invoices', 'price',
            'effective_from', 'effective_to', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProformaInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for ProformaInvoice model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ProformaInvoice
        fields = [
            'id', 'invoice_number', 'user', 'user_email', 'amount',
            'tax_amount', 'total_amount', 'gst_rate', 'service_type',
            'description', 'status', 'valid_until', 'is_expired',
            'related_filing_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'user', 'created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class ProformaInvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating proforma invoice."""
    
    class Meta:
        model = ProformaInvoice
        fields = ['user', 'amount', 'service_type', 'description', 'related_filing_id']
    
    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        
        proforma = ProformaInvoice.objects.create(**validated_data)
        proforma.valid_until = timezone.now() + timedelta(days=15)  # 15 days validity
        proforma.save()
        return proforma


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'proforma', 'user', 'user_email',
            'amount', 'tax_amount', 'total_amount', 'service_type',
            'description', 'status', 'payment_method', 'payment_reference',
            'paid_at', 'pdf_file', 'due_date', 'days_until_due', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'user', 'created_at', 'updated_at', 'paid_at'
        ]
    
    def get_days_until_due(self, obj):
        from datetime import date
        if obj.status == 'paid':
            return None
        due_date = obj.due_date
        if isinstance(due_date, str):
            from dateutil import parser
            due_date = parser.parse(due_date).date()
        return (due_date - date.today()).days
    
    def get_is_overdue(self, obj):
        if obj.status == 'paid':
            return False
        from datetime import date
        due_date = obj.due_date
        if isinstance(due_date, str):
            from dateutil import parser
            due_date = parser.parse(due_date).date()
        return date.today() > due_date


class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for PaymentRecord model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'user', 'user_email', 'invoice', 'proforma', 'amount',
            'currency', 'gateway', 'gateway_payment_id', 'status',
            'payment_method', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentInitSerializer(serializers.Serializer):
    """Serializer for initiating payment."""
    
    invoice_id = serializers.UUIDField(required=False)
    proforma_id = serializers.UUIDField(required=False)
    gateway = serializers.ChoiceField(choices=['razorpay', 'cashfree', 'stripe'])
    
    def validate(self, attrs):
        if not attrs.get('invoice_id') and not attrs.get('proforma_id'):
            raise serializers.ValidationError(
                'Either invoice_id or proforma_id is required.'
            )
        return attrs


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for payment gateway webhooks."""
    
    gateway = serializers.ChoiceField(choices=['razorpay', 'cashfree', 'stripe'])
    event = serializers.CharField()
    data = serializers.DictField()
