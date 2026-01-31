"""
Business Services models for GSTONGO.
Includes: Company Incorporation, FSSAI, MSME/Udyam, PAN/TAN
"""
import uuid
from django.db import models
from django.conf import settings


class ServiceApplication(models.Model):
    """Base model for all business service applications."""
    
    SERVICE_TYPES = [
        ('company_incorporation', 'Company Incorporation'),
        ('fssai_registration', 'FSSAI Registration'),
        ('msme_registration', 'MSME/Udyam Registration'),
        ('pan_application', 'PAN Application'),
        ('tan_application', 'TAN Application'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('documents_pending', 'Documents Pending'),
        ('under_review', 'Under Review'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_applications'
    )
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Application data stored as JSON
    application_data = models.JSONField(default=dict)
    
    # Admin notes
    admin_notes = models.TextField(blank=True, null=True)
    
    # Reference numbers
    application_reference = models.CharField(max_length=50, unique=True)
    certificate_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_applications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.application_reference}"


class CompanyIncorporation(models.Model):
    """Company Incorporation specific details."""
    
    COMPANY_TYPES = [
        ('pvt_ltd', 'Private Limited'),
        ('llp', 'LLP'),
        ('opc', 'One Person Company'),
        ('public', 'Public Limited'),
        ('section_8', 'Section 8 Company'),
    ]
    
    application = models.OneToOneField(ServiceApplication, on_delete=models.CASCADE, related_name='company_details')
    
    proposed_name_1 = models.CharField(max_length=200)
    proposed_name_2 = models.CharField(max_length=200, blank=True)
    proposed_name_3 = models.CharField(max_length=200, blank=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    
    authorized_capital = models.DecimalField(max_digits=15, decimal_places=2)
    paid_up_capital = models.DecimalField(max_digits=15, decimal_places=2)
    
    registered_address = models.TextField()
    business_activity = models.TextField()
    
    # Directors info stored in JSON
    directors_data = models.JSONField(default=list)
    
    # Status from MCA
    name_approval_status = models.CharField(max_length=50, null=True, blank=True)
    cin = models.CharField(max_length=25, null=True, blank=True)
    
    class Meta:
        db_table = 'company_incorporations'


class FSSAIRegistration(models.Model):
    """FSSAI Registration specific details."""
    
    LICENSE_TYPES = [
        ('basic', 'Basic Registration'),
        ('state', 'State License'),
        ('central', 'Central License'),
    ]
    
    application = models.OneToOneField(ServiceApplication, on_delete=models.CASCADE, related_name='fssai_details')
    
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES)
    business_name = models.CharField(max_length=200)
    food_category = models.CharField(max_length=200)
    
    premise_address = models.TextField()
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2)
    
    fssai_license_number = models.CharField(max_length=20, null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'fssai_registrations'


class MSMERegistration(models.Model):
    """MSME/Udyam Registration specific details."""
    
    ENTERPRISE_TYPES = [
        ('micro', 'Micro'),
        ('small', 'Small'),
        ('medium', 'Medium'),
    ]
    
    application = models.OneToOneField(ServiceApplication, on_delete=models.CASCADE, related_name='msme_details')
    
    enterprise_name = models.CharField(max_length=200)
    enterprise_type = models.CharField(max_length=20, choices=ENTERPRISE_TYPES)
    
    nic_code = models.CharField(max_length=10)
    major_activity = models.CharField(max_length=200)
    
    plant_address = models.TextField()
    investment_in_plant = models.DecimalField(max_digits=15, decimal_places=2)
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2)
    
    udyam_number = models.CharField(max_length=25, null=True, blank=True)
    
    class Meta:
        db_table = 'msme_registrations'


class PANTANApplication(models.Model):
    """PAN/TAN Application details."""
    
    APPLICATION_TYPES = [
        ('pan_new', 'New PAN'),
        ('pan_correction', 'PAN Correction'),
        ('tan_new', 'New TAN'),
        ('tan_correction', 'TAN Correction'),
    ]
    
    application = models.OneToOneField(ServiceApplication, on_delete=models.CASCADE, related_name='pantan_details')
    
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    
    # Applicant details
    applicant_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # For corrections
    existing_pan = models.CharField(max_length=10, blank=True)
    existing_tan = models.CharField(max_length=10, blank=True)
    
    # Issued number
    issued_pan = models.CharField(max_length=10, null=True, blank=True)
    issued_tan = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'pantan_applications'


class ServiceDocument(models.Model):
    """Documents for service applications."""
    
    DOCUMENT_TYPES = [
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('photo', 'Photograph'),
        ('moa', 'MOA'),
        ('aoa', 'AOA'),
        ('rent_agreement', 'Rent Agreement'),
        ('noc', 'NOC'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(ServiceApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='service_documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_documents'
