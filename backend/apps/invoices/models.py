"""
Invoice models for payment processing.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class RateSlab(models.Model):
    """Rate slab configuration for pricing."""
    
    name = models.CharField(max_length=100)
    min_invoices = models.IntegerField()
    max_invoices = models.IntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rate_slabs'
        verbose_name = 'Rate Slab'
        verbose_name_plural = 'Rate Slabs'
    
    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.min_invoices}-{self.max_invoices} invoices)"


class ProformaInvoice(models.Model):
    """Proforma invoice model."""
    
    INVOICE_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proforma_invoices'
    )
    
    # Invoice details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    
    # Service details
    service_type = models.CharField(max_length=100, default='GST Filing')
    description = models.TextField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='pending')
    
    # Expiry
    valid_until = models.DateTimeField()
    
    # Generated from filing
    related_filing_id = models.UUIDField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proforma_invoices'
        verbose_name = 'Proforma Invoice'
        verbose_name_plural = 'Proforma Invoices'
    
    def __str__(self):
        return f"Proforma {self.invoice_number} - {self.user.email} - ₹{self.total_amount}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        self.tax_amount = self.total_amount - self.amount
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number."""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m%d')
        return f"PI-{date_str}-{uuid.uuid4().hex[:6].upper()}"
    
    def is_expired(self):
        """Check if proforma is expired."""
        from django.utils import timezone
        return timezone.now() > self.valid_until


class Invoice(models.FriendlyFilenameMixin, models.Model):
    """Final invoice model (generated from proforma)."""
    
    INVOICE_STATUS = [
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('online', 'Online Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    proforma = models.OneToOneField(
        ProformaInvoice,
        on_delete=models.SET_NULL,
        null=True,
        related_name='final_invoice'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Invoice details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Service details
    service_type = models.CharField(max_length=100, default='GST Filing')
    description = models.TextField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='issued')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # PDF file
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Due date
    due_date = models.DateField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.email} - ₹{self.total_amount}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        self.tax_amount = self.total_amount - self.amount
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number."""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m%d')
        return f"INV-{date_str}-{uuid.uuid4().hex[:6].upper()}"
    
    def mark_as_paid(self, method, reference):
        """Mark invoice as paid."""
        from django.utils import timezone
        self.status = 'paid'
        self.payment_method = method
        self.payment_reference = reference
        self.paid_at = timezone.now()
        self.save()
        
        # Update proforma if exists
        if self.proforma:
            self.proforma.status = 'paid'
            self.proforma.save()


class PaymentRecord(models.Model):
    """Record of all payments."""
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_GATEWAYS = [
        ('razorpay', 'Razorpay'),
        ('cashfree', 'Cashfree'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_records'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    proforma = models.ForeignKey(
        ProformaInvoice,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAYS)
    gateway_payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Metadata
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    webhook_data = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_records'
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.email} - ₹{self.amount}"
