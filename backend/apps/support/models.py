"""
Support & Ticketing System models for GSTONGO.
Includes: Enquiry Management, Support Tickets, Job Tickets
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Enquiry(models.Model):
    """Public enquiry form submissions."""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]
    
    SERVICE_INTERESTS = [
        ('gst_filing', 'GST Filing'),
        ('itr_filing', 'Income Tax Filing'),
        ('tds_filing', 'TDS Filing'),
        ('company_incorporation', 'Company Incorporation'),
        ('fssai', 'FSSAI Registration'),
        ('msme', 'MSME Registration'),
        ('pan_tan', 'PAN/TAN Services'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contact details
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    
    # Enquiry details
    service_interest = models.CharField(max_length=30, choices=SERVICE_INTERESTS)
    message = models.TextField()
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_enquiries'
    )
    
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Source tracking
    source = models.CharField(max_length=50, default='website')
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enquiries'
        verbose_name_plural = 'Enquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.service_interest}"


class SupportTicket(models.Model):
    """Customer support tickets."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting for Customer'),
        ('waiting_internal', 'Waiting for Internal'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('billing', 'Billing'),
        ('technical', 'Technical'),
        ('service', 'Service Related'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True)
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    
    subject = models.CharField(max_length=300)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tickets'
    )
    
    # SLA tracking
    sla_due = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)
    
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Rating
    rating = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"


class TicketComment(models.Model):
    """Comments/replies on support tickets."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments')
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_comments'
    )
    
    message = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes not visible to customer
    
    attachment = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ticket_comments'
        ordering = ['created_at']


class JobTicket(models.Model):
    """Internal job tickets for service processing."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    JOB_TYPES = [
        ('gst_filing', 'GST Filing'),
        ('itr_filing', 'ITR Filing'),
        ('tds_filing', 'TDS Filing'),
        ('company_reg', 'Company Registration'),
        ('fssai_reg', 'FSSAI Registration'),
        ('msme_reg', 'MSME Registration'),
        ('pan_application', 'PAN Application'),
        ('tan_application', 'TAN Application'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_number = models.CharField(max_length=20, unique=True)
    
    # Customer reference
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_tickets'
    )
    
    # Job details
    title = models.CharField(max_length=300)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_jobs'
    )
    team = models.CharField(max_length=100, blank=True)
    
    # Timeline
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    due_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Time tracking
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Quality
    quality_score = models.PositiveIntegerField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.job_number} - {self.title}"


class JobTask(models.Model):
    """Sub-tasks within a job ticket."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobTicket, on_delete=models.CASCADE, related_name='tasks')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tasks'
    )
    
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_tasks'
        ordering = ['order']


class KnowledgeBase(models.Model):
    """FAQ and knowledge base articles."""
    
    CATEGORY_CHOICES = [
        ('gst', 'GST'),
        ('itr', 'Income Tax'),
        ('tds', 'TDS'),
        ('company', 'Company Registration'),
        ('fssai', 'FSSAI'),
        ('msme', 'MSME'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    question = models.TextField()  # For FAQ
    content = models.TextField()
    
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    views = models.PositiveIntegerField(default=0)
    helpful_votes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'knowledge_base'
        ordering = ['-is_featured', '-views']
    
    def __str__(self):
        return self.title
