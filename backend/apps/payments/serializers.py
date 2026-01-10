"""
Serializers for Payment app.
"""
from rest_framework import serializers


class PaymentInitSerializer(serializers.Serializer):
    """Serializer for payment initialization."""
    
    invoice_id = serializers.UUIDField(required=False)
    proforma_id = serializers.UUIDField(required=False)
    gateway = serializers.ChoiceField(
        choices=['razorpay', 'cashfree', 'stripe'],
        default='razorpay'
    )
    
    def validate(self, attrs):
        """Ensure either invoice_id or proforma_id is provided."""
        if not attrs.get('invoice_id') and not attrs.get('proforma_id'):
            raise serializers.ValidationError(
                'Either invoice_id or proforma_id is required.'
            )
        return attrs


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for payment verification."""
    
    razorpay_payment_id = serializers.CharField(required=True)
    razorpay_order_id = serializers.CharField(required=True)
    razorpay_signature = serializers.CharField(required=True)
    transaction_id = serializers.IntegerField(required=False)


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for payment webhook."""
    
    event = serializers.CharField()
    payload = serializers.DictField()


class PaymentTransactionSerializer(serializers.Serializer):
    """Serializer for payment transaction."""
    
    id = serializers.UUIDField()
    invoice_number = serializers.CharField(allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    gateway = serializers.CharField()
    transaction_id = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)


class RefundSerializer(serializers.Serializer):
    """Serializer for refund request."""
    
    payment_id = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text='Refund amount (optional, defaults to full payment)'
    )
    reason = serializers.CharField(required=False)


class PaymentMethodSerializer(serializers.Serializer):
    """Serializer for saved payment methods."""
    
    id = serializers.CharField()
    type = serializers.CharField()
    bank = serializers.CharField(allow_null=True)
    last4 = serializers.CharField(allow_null=True)
    exp_month = serializers.IntegerField(allow_null=True)
    exp_year = serializers.IntegerField(allow_null=True)
    is_default = serializers.BooleanField(default=False)
