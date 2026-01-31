"""
Document Vault models for GSTONGO.
Centralized document management system.
"""
import uuid
from django.db import models
from django.conf import settings


class DocumentCategory(models.Model):
    """Categories for organizing documents."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='folder')
    
    class Meta:
        db_table = 'document_categories'
        verbose_name_plural = 'Document Categories'
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """User document storage."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_documents'
    )
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, related_name='documents')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='document_vault/%Y/%m/%d/')
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()  # in bytes
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Expiration tracking
    expiry_date = models.DateField(null=True, blank=True)
    expiry_reminder_sent = models.BooleanField(default=False)
    
    # Tags for better organization
    tags = models.JSONField(default=list)
    
    # OCR extracted text
    extracted_text = models.TextField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vault_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"


class DocumentShare(models.Model):
    """Sharing documents with others."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    
    share_token = models.CharField(max_length=100, unique=True)
    shared_with_email = models.EmailField(null=True, blank=True)
    
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    access_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_shares'


class OrderTracking(models.Model):
    """Order tracking for all services."""
    
    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('documents_received', 'Documents Received'),
        ('processing', 'Processing'),
        ('under_review', 'Under Review'),
        ('pending_approval', 'Pending Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    order_reference = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=50)
    service_name = models.CharField(max_length=200)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='placed')
    current_step = models.PositiveIntegerField(default=1)
    total_steps = models.PositiveIntegerField(default=5)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    
    estimated_completion = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_tracking'
        ordering = ['-created_at']


class OrderMilestone(models.Model):
    """Milestones for order tracking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, related_name='milestones')
    
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_milestones'
        ordering = ['step_number']
