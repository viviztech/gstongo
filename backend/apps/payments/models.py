"""
Payment Transaction Model
"""
import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class PaymentTransaction(models.Model):
    """Model for tracking payment transactions."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    GATEWAY_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('cashfree', 'Cashfree'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_transactions'
    )
    
    # Related documents
    invoice = models.ForeignKey(
        'invoices.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    proforma = models.ForeignKey(
        'invoices.ProformaInvoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    # Payment gateway details
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    gateway_order_id = models.CharField(max_length=100, unique=True)
    gateway_payment_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_refund_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Error tracking
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Signature (for verification)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_transactions'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.id} - ₹{self.amount} ({self.status})"
    
    def mark_as_success(self, payment_id: str = None):
        """Mark transaction as successful."""
        from django.utils import timezone
        self.status = 'success'
        self.completed_at = timezone.now()
        if payment_id:
            self.gateway_payment_id = payment_id
        self.save()
    
    def mark_as_failed(self, error_message: str):
        """Mark transaction as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
    
    def mark_as_refunded(self, refund_id: str, amount: Decimal):
        """Mark transaction as refunded."""
        from django.utils import timezone
        self.status = 'refunded'
        self.gateway_refund_id = refund_id
        self.refund_amount = amount
        self.save()
