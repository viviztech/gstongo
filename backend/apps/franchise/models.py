"""
Franchise Management System models for GSTONGO.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Franchise(models.Model):
    """Franchise partner model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ]
    
    FRANCHISE_TYPES = [
        ('individual', 'Individual'),
        ('partnership', 'Partnership'),
        ('company', 'Company'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='franchise'
    )
    
    # Business details
    franchise_code = models.CharField(max_length=20, unique=True)
    business_name = models.CharField(max_length=200)
    franchise_type = models.CharField(max_length=20, choices=FRANCHISE_TYPES)
    
    # Contact
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # KYC
    pan_number = models.CharField(max_length=10)
    gst_number = models.CharField(max_length=15, blank=True)
    bank_account_number = models.CharField(max_length=20)
    bank_ifsc = models.CharField(max_length=11)
    kyc_verified = models.BooleanField(default=False)
    
    # Agreement
    agreement_signed = models.BooleanField(default=False)
    agreement_date = models.DateField(null=True, blank=True)
    agreement_expiry = models.DateField(null=True, blank=True)
    
    # Financials
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # percentage
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Performance
    total_customers = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'franchises'
        verbose_name_plural = 'Franchises'
    
    def __str__(self):
        return f"{self.franchise_code} - {self.business_name}"


class FranchiseTerritory(models.Model):
    """Territory assigned to a franchise."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name='territories')
    
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    pincode_start = models.CharField(max_length=6)
    pincode_end = models.CharField(max_length=6)
    
    is_exclusive = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'franchise_territories'


class FranchiseCommission(models.Model):
    """Commission records for franchises."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name='commissions')
    
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    
    gross_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_payable = models.DecimalField(max_digits=15, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'franchise_commissions'
        unique_together = ['franchise', 'month', 'year']


class PincodeMapping(models.Model):
    """Pincode to franchise mapping for customer routing."""
    
    pincode = models.CharField(max_length=6, unique=True)
    franchise = models.ForeignKey(Franchise, on_delete=models.SET_NULL, null=True, related_name='pincodes')
    
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)  # For load balancing
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'franchise_pincode_mappings'
    
    def __str__(self):
        return f"{self.pincode} - {self.district}, {self.state}"


class CustomerAssignment(models.Model):
    """Customer to franchise assignment."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='franchise_assignments'
    )
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name='assigned_customers')
    
    assigned_by = models.CharField(max_length=20)  # 'auto' or 'manual'
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'customer_assignments'
        unique_together = ['customer', 'franchise']
