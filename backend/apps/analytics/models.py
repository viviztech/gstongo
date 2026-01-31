"""
Analytics and Reporting models for GSTONGO.
Business Intelligence, Predictive Analytics, and Report Generation.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ReportTemplate(models.Model):
    """Customizable report templates."""
    
    REPORT_TYPES = [
        ('revenue', 'Revenue Report'),
        ('filings', 'Filings Report'),
        ('customer', 'Customer Report'),
        ('franchise', 'Franchise Report'),
        ('service', 'Service Report'),
        ('performance', 'Performance Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    # Query configuration (JSON)
    query_config = models.JSONField(default=dict)
    columns = models.JSONField(default=list)  # Selected columns
    filters = models.JSONField(default=dict)  # Default filters
    
    default_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    is_public = models.BooleanField(default=False)  # Available to all users
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_templates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
    
    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """Generated reports for download/email."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20)
    format = models.CharField(max_length=10)
    
    parameters = models.JSONField(default=dict)  # Report parameters used
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file = models.FileField(upload_to='generated_reports/%Y/%m/%d/', null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'generated_reports'
        ordering = ['-created_at']


class ScheduledReport(models.Model):
    """Scheduled reports for automatic generation."""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules')
    
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Schedule configuration
    day_of_week = models.PositiveIntegerField(null=True, blank=True)  # 0-6 for weekly
    day_of_month = models.PositiveIntegerField(null=True, blank=True)  # 1-31 for monthly
    time = models.TimeField()
    
    recipients = models.JSONField(default=list)  # Email addresses
    
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduled_reports'


class DashboardWidget(models.Model):
    """Customizable dashboard widgets."""
    
    WIDGET_TYPES = [
        ('metric', 'Single Metric'),
        ('chart_line', 'Line Chart'),
        ('chart_bar', 'Bar Chart'),
        ('chart_pie', 'Pie Chart'),
        ('table', 'Data Table'),
        ('list', 'List'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    
    # Data source configuration
    data_source = models.CharField(max_length=100)  # Model name or API
    query_config = models.JSONField(default=dict)
    
    # Display options
    display_config = models.JSONField(default=dict)  # Colors, labels, etc.
    
    # Position in dashboard
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'


class UserDashboard(models.Model):
    """User's custom dashboard configuration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_dashboard'
    )
    
    name = models.CharField(max_length=200, default='My Dashboard')
    widgets = models.ManyToManyField(DashboardWidget, related_name='dashboards')
    layout = models.JSONField(default=dict)  # Widget positions
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_dashboards'


class AuditLog(models.Model):
    """Comprehensive audit logging."""
    
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('access', 'Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True)
    
    details = models.JSONField(default=dict)  # Action-specific details
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]


class APIKey(models.Model):
    """API keys for third-party integrations."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=64, unique=True)
    key_prefix = models.CharField(max_length=8)  # First 8 chars for identification
    
    permissions = models.JSONField(default=list)  # List of allowed endpoints
    rate_limit = models.PositiveIntegerField(default=1000)  # Requests per hour
    
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    request_count = models.PositiveIntegerField(default=0)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_keys'


class Webhook(models.Model):
    """Webhook configurations for events."""
    
    EVENT_CHOICES = [
        ('filing.created', 'Filing Created'),
        ('filing.completed', 'Filing Completed'),
        ('payment.received', 'Payment Received'),
        ('order.updated', 'Order Updated'),
        ('ticket.created', 'Ticket Created'),
        ('ticket.resolved', 'Ticket Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    
    name = models.CharField(max_length=200)
    url = models.URLField()
    events = models.JSONField(default=list)  # List of event types
    
    secret = models.CharField(max_length=64)  # For signature verification
    
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    failed_deliveries = models.PositiveIntegerField(default=0)
    
    last_delivery = models.DateTimeField(null=True, blank=True)
    last_response_code = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhooks'
