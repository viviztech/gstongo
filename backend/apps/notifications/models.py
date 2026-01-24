"""
Notification models for GSTONGO.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class NotificationTemplate(models.Model):
    """Notification template for consistent messaging."""
    
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    NOTIFICATION_CATEGORIES = [
        ('registration', 'Registration'),
        ('otp', 'OTP'),
        ('filing_reminder', 'Filing Reminder'),
        ('filing_status', 'Filing Status'),
        ('payment_reminder', 'Payment Reminder'),
        ('payment_received', 'Payment Received'),
        ('invoice_generated', 'Invoice Generated'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=30, choices=NOTIFICATION_CATEGORIES)
    
    # Template content
    subject = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField()
    
    # Variables that can be used in template
    variables = models.JSONField(default=list, help_text='List of variable names')
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class Notification(models.Model):
    """User notification model."""
    
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification details
    channel = models.CharField(max_length=20, choices=NOTIFICATION_CHANNELS)
    category = models.CharField(max_length=30, choices=NotificationTemplate.NOTIFICATION_CATEGORIES)
    
    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Reference
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Template used (if any)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.user.email} - {self.status}"


class NotificationSchedule(models.Model):
    """Scheduled notification rules."""
    
    SCHEDULE_TYPES = [
        ('one_time', 'One Time'),
        ('recurring', 'Recurring'),
    ]
    
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    TRIGGER_TYPES = [
        ('date_based', 'Date Based'),
        ('filing_based', 'Filing Based'),
        ('payment_based', 'Payment Based'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='one_time')
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, null=True, blank=True)
    
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_days = models.IntegerField(
        default=0,
        help_text='Days before/after trigger event'
    )
    
    # Template to use
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Targeting
    target_all_users = models.BooleanField(default=True)
    target_gst_filing_due = models.BooleanField(default=False)
    target_payment_overdue = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    # Execution tracking
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_schedules'
        verbose_name = 'Notification Schedule'
        verbose_name_plural = 'Notification Schedules'
    
    def __str__(self):
        return f"{self.name} ({self.trigger_type})"


class FCMToken(models.Model):
    """Firebase Cloud Messaging tokens for push notifications."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_tokens'
    )
    token = models.CharField(max_length=500, unique=True)
    device_type = models.CharField(max_length=20, default='android')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fcm_tokens'
        verbose_name = 'FCM Token'
        verbose_name_plural = 'FCM Tokens'
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type}"
