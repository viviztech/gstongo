"""
TDS (Tax Deducted at Source) Filing models for GSTONGO.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TDSReturn(models.Model):
    """Model for TDS Return filing."""
    
    RETURN_TYPES = [
        ('24Q', 'Form 24Q - Salary'),
        ('26Q', 'Form 26Q - Non-Salary'),
        ('27Q', 'Form 27Q - NRI Payments'),
        ('27EQ', 'Form 27EQ - TCS'),
    ]
    
    QUARTER_CHOICES = [
        ('Q1', 'Q1 (Apr-Jun)'),
        ('Q2', 'Q2 (Jul-Sep)'),
        ('Q3', 'Q3 (Oct-Dec)'),
        ('Q4', 'Q4 (Jan-Mar)'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tds_returns'
    )
    return_type = models.CharField(max_length=10, choices=RETURN_TYPES)
    financial_year = models.CharField(max_length=7)
    quarter = models.CharField(max_length=5, choices=QUARTER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Deductor details
    tan_number = models.CharField(max_length=10)
    deductor_name = models.CharField(max_length=200)
    
    # Summary
    total_deducted = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Filing reference
    acknowledgment_number = models.CharField(max_length=50, null=True, blank=True)
    filed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tds_returns'
        unique_together = ['user', 'return_type', 'financial_year', 'quarter']
    
    def __str__(self):
        return f"{self.return_type} - {self.financial_year} - {self.quarter}"


class TDSDeductee(models.Model):
    """Deductee details for TDS return."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tds_return = models.ForeignKey(TDSReturn, on_delete=models.CASCADE, related_name='deductees')
    
    pan = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    section_code = models.CharField(max_length=10)
    date_of_payment = models.DateField()
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    tds_deducted = models.DecimalField(max_digits=15, decimal_places=2)
    tds_deposited = models.DecimalField(max_digits=15, decimal_places=2)
    challan_number = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tds_deductees'


class TDSChallan(models.Model):
    """TDS Challan payment details."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tds_return = models.ForeignKey(TDSReturn, on_delete=models.CASCADE, related_name='challans')
    
    challan_number = models.CharField(max_length=20)
    bsr_code = models.CharField(max_length=10)
    challan_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    challan_type = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tds_challans'
