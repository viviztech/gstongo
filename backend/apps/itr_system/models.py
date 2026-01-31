"""
Income Tax Return (ITR) models for GSTONGO.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ITRFiling(models.Model):
    """Base model for Income Tax Return fillings."""
    
    ITR_TYPES = [
        ('ITR1', 'ITR-1 (Sahaj)'),
        ('ITR2', 'ITR-2'),
        ('ITR3', 'ITR-3'),
        ('ITR4', 'ITR-4 (Sugam)'),
    ]
    
    FILING_STATUS = [
        ('draft', 'Draft'),
        ('pending_verification', 'Pending Verification'),
        ('verified', 'Verified'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='itr_filings'
    )
    filing_type = models.CharField(max_length=10, choices=ITR_TYPES)
    financial_year = models.CharField(max_length=7)  # e.g., '2024-25'
    assessment_year = models.CharField(max_length=7)  # e.g., '2025-26'
    
    # Filing status
    status = models.CharField(max_length=25, choices=FILING_STATUS, default='draft')
    
    # Summary Data
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_due = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Filing reference
    acknowledgment_number = models.CharField(max_length=50, null=True, blank=True)
    filed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'itr_filings'
        verbose_name = 'ITR Filing'
        verbose_name_plural = 'ITR Filings'
        unique_together = ['user', 'financial_year', 'filing_type']
    
    def __str__(self):
        return f"{self.filing_type} - {self.user.email} - {self.financial_year}"


class ITR1Details(models.Model):
    """Specific details for ITR-1 (For individuals having income from salaries, one house property, other sources)."""
    
    filing = models.OneToOneField(ITRFiling, on_delete=models.CASCADE, related_name='itr1_details')
    
    # Part B - Gross Total Income
    salary_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    house_property_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_sources_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Part C - Deductions and Taxable Total Income
    deduction_80c = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deduction_80d = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Part D - Computation of Tax Payable
    tax_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    rebate_87a = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    surcharge = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    health_education_cess = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # JSON data for complete form storage
    form_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'itr1_details'
        verbose_name = 'ITR-1 Detail'
        verbose_name_plural = 'ITR-1 Details'


class ITRDocument(models.Model):
    """Documents uploaded for ITR filing (Form 16, Bank statements, etc.)."""
    
    DOCUMENT_TYPES = [
        ('form_16', 'Form 16'),
        ('bank_statement', 'Bank Statement'),
        ('investment_proof', 'Investment Proof'),
        ('pan_card', 'PAN Card'),
        ('aadhaar_card', 'Aadhaar Card'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filing = models.ForeignKey(ITRFiling, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='itr_documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'itr_documents'
        verbose_name = 'ITR Document'
        verbose_name_plural = 'ITR Documents'
