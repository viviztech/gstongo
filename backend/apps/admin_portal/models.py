"""
Admin Portal models.
"""
import uuid
from django.db import models
from django.conf import settings


class AdminDashboardStats(models.Model):
    """Daily dashboard statistics snapshot."""
    
    date = models.DateField(unique=True)
    
    # User stats
    new_users = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    
    # Filing stats
    gstr1_filed = models.IntegerField(default=0)
    gstr3b_filed = models.IntegerField(default=0)
    gstr9b_filed = models.IntegerField(default=0)
    nil_filings = models.IntegerField(default=0)
    
    # Payment stats
    payments_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pending_invoices = models.IntegerField(default=0)
    overdue_invoices = models.IntegerField(default=0)
    overdue_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_dashboard_stats'
        verbose_name = 'Dashboard Statistics'
        verbose_name_plural = 'Dashboard Statistics'
    
    def __str__(self):
        return f"Stats for {self.date}"


class UserSearchHistory(models.Model):
    """Track admin user searches."""
    
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    search_type = models.CharField(max_length=50)  # 'cin', 'gst', 'name', 'email'
    search_value = models.CharField(max_length=255)
    result_count = models.IntegerField()
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_search_history'
        verbose_name = 'User Search History'
        verbose_name_plural = 'User Search Histories'
    
    def __str__(self):
        return f"{self.admin.email} searched {self.search_value}"


class AdminActivityLog(models.Model):
    """Log admin activities."""
    
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_type = models.CharField(max_length=50)  # 'user', 'filing', 'invoice', etc.
    target_id = models.UUIDField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_activity_logs'
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.email} - {self.action} - {self.target_type}"


class SystemSettings(models.Model):
    """System-wide settings managed by admins."""
    
    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    description = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_typed_value(self):
        """Return value in correct type."""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.setting_type == 'integer':
            return int(self.value)
        elif self.setting_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class PincodeMapping(models.Model):
    """Map pincodes to regions/admins/franchises."""
    
    pincode = models.CharField(max_length=6, unique=True)
    region_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, null=True, blank=True)
    
    # Assignment
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pincodes'
    )
    assigned_franchise = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_pincodes'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pincode_mappings'
        verbose_name = 'Pincode Mapping'
        verbose_name_plural = 'Pincode Mappings'
    
    def __str__(self):
        return f"{self.pincode} - {self.region_name}"
