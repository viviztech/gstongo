"""
GST Filing models for GSTONGO.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class GSTFiling(models.Model):
    """Base model for GST filings."""
    
    FILING_TYPES = [
        ('GSTR1', 'GSTR-1 - Outward Supplies'),
        ('GSTR3B', 'GSTR-3B - Summary Return'),
        ('GSTR9B', 'GSTR-9B - Annual Return'),
    ]
    
    FILING_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected'),
    ]
    
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gst_filings'
    )
    filing_type = models.CharField(max_length=10, choices=FILING_TYPES)
    financial_year = models.CharField(max_length=4)  # e.g., '2024-25'
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    
    # Filing status
    status = models.CharField(max_length=20, choices=FILING_STATUS, default='draft')
    
    # Data fields
    nil_filing = models.BooleanField(default=False)
    total_taxable_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    total_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Declaration
    declaration_statement = models.TextField(null=True, blank=True)
    declaration_signed = models.BooleanField(default=False)
    declaration_signed_at = models.DateTimeField(null=True, blank=True)
    
    # Filing reference (from GST portal)
    filing_reference_number = models.CharField(max_length=50, null=True, blank=True)
    filed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin control
    filing_locked = models.BooleanField(default=False)
    lock_reason = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gst_filings'
        verbose_name = 'GST Filing'
        verbose_name_plural = 'GST Filings'
        unique_together = ['user', 'filing_type', 'financial_year', 'month']
    
    def __str__(self):
        return f"{self.filing_type} - {self.user.email} - {self.financial_year} - {self.month}"
    
    def mark_as_filed(self, reference_number):
        """Mark filing as filed."""
        self.status = 'filed'
        self.filing_reference_number = reference_number
        self.filed_at = timezone.now()
        self.save()


class GSTR1Details(models.Model):
    """GSTR-1 specific details."""
    
    filing = models.OneToOneField(
        GSTFiling,
        on_delete=models.CASCADE,
        related_name='gstr1_details'
    )
    
    # B2B Invoices (4-digit HSN)
    b2b_invoices_count = models.IntegerField(default=0)
    b2b_invoices_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    b2b_invoices_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # B2C Invoices (6-digit HSN)
    b2c_invoices_count = models.IntegerField(default=0)
    b2c_invoices_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    b2c_invoices_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Exports
    export_invoices_count = models.IntegerField(default=0)
    export_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Nil Rated / Exempted
    nil_rated_invoices_count = models.IntegerField(default=0)
    nil_rated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Debit/Credit Notes
    debit_notes_count = models.IntegerField(default=0)
    credit_notes_count = models.IntegerField(default=0)
    net_notes_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # JSON data storage for complete filing data
    invoice_data = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gstr1_details'
        verbose_name = 'GSTR-1 Details'
    
    def __str__(self):
        return f"GSTR-1 Details for {self.filing}"


class GSTR3BDetails(models.Model):
    """GSTR-3B specific details."""
    
    filing = models.OneToOneField(
        GSTFiling,
        on_delete=models.CASCADE,
        related_name='gstr3b_details'
    )
    
    # Outward Supplies
    outward_taxable_supplies = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outward_tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Inward Supplies (Reversal)
    inward_supplies = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    itc_reversal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Input Tax Credit
    igst_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cgst_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sgst_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Tax Liability
    igst_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cgst_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sgst_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cess_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Interest and Late Fee
    interest_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    late_fee_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # JSON data storage
    tax_data = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gstr3b_details'
        verbose_name = 'GSTR-3B Details'
    
    def __str__(self):
        return f"GSTR-3B Details for {self.filing}"


class GSTR9BDetails(models.Model):
    """GSTR-9B Annual Return details."""
    
    filing = models.OneToOneField(
        GSTFiling,
        on_delete=models.CASCADE,
        related_name='gstr9b_details'
    )
    
    # Annual Summary
    total_outward_supplies = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_inward_supplies = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # ITC Summary
    total_itc_claimed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    itc_reversed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_itc = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # JSON data storage
    annual_data = models.JSONField(null=True, blank=True)
    
    # Audit details
    auditor_name = models.CharField(max_length=255, null=True, blank=True)
    auditor_membership_number = models.CharField(max_length=50, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gstr9b_details'
        verbose_name = 'GSTR-9B Details'
    
    def __str__(self):
        return f"GSTR-9B Details for {self.filing}"


class Invoice(models.Model):
    """Model for storing invoice data for GST filing."""
    
    INVOICE_TYPE_CHOICES = [
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
        ('export', 'Export'),
        ('debit_note', 'Debit Note'),
        ('credit_note', 'Credit Note'),
        ('import', 'Import'),
    ]
    
    filing = models.ForeignKey(
        GSTFiling,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    invoice_number = models.CharField(max_length=50)
    invoice_date = models.DateField()
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    
    # Counterparty details
    counterparty_gstin = models.CharField(max_length=15, null=True, blank=True)
    counterparty_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Invoice values
    taxable_value = models.DecimalField(max_digits=15, decimal_places=2)
    igst = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cess = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # HSN/SAC code
    hsn_code = models.CharField(max_length=10, null=True, blank=True)
    
    # Export details
    export_port = models.CharField(max_length=100, null=True, blank=True)
    shipping_bill_number = models.CharField(max_length=50, null=True, blank=True)
    shipping_bill_date = models.DateField(null=True, blank=True)
    
    # Note details (for credit/debit notes)
    original_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    original_invoice_date = models.DateField(null=True, blank=True)
    note_reason = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.filing}"


class FilingDocument(models.Model):
    """Model for storing filing-related documents."""
    
    filing = models.ForeignKey(
        GSTFiling,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='filing_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'filing_documents'
        verbose_name = 'Filing Document'
        verbose_name_plural = 'Filing Documents'
    
    def __str__(self):
        return f"{self.document_type} - {self.filing}"
