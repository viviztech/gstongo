"""
Serializers for Admin Portal.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    AdminDashboardStats, UserSearchHistory, AdminActivityLog,
    SystemSettings, PincodeMapping
)
from apps.users.models import User
from apps.gst_filing.models import GSTFiling
from apps.invoices.models import Invoice, ProformaInvoice

User = get_user_model()


class DashboardStatsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard statistics."""
    
    class Meta:
        model = AdminDashboardStats
        fields = [
            'date', 'new_users', 'total_users',
            'gstr1_filed', 'gstr3b_filed', 'gstr9b_filed', 'nil_filings',
            'payments_collected', 'pending_invoices', 'overdue_invoices', 'overdue_amount',
            'created_at'
        ]


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data."""
    
    # User stats
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    new_users_this_month = serializers.IntegerField()
    
    # Filing stats
    total_filings = serializers.IntegerField()
    pending_filings = serializers.IntegerField()
    filed_today = serializers.IntegerField()
    nil_filings_count = serializers.IntegerField()
    
    # Payment stats
    total_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_count = serializers.IntegerField()
    overdue_amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class UserSearchSerializer(serializers.Serializer):
    """Serializer for user search."""
    
    search_type = serializers.ChoiceField(
        choices=['cin', 'gst', 'name', 'email', 'phone', 'pincode']
    )
    search_value = serializers.CharField()
    
    def validate_search_value(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Search value must be at least 2 characters.')
        return value


class UserSearchResultSerializer(serializers.Serializer):
    """Serializer for user search results."""
    
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    cin = serializers.CharField()
    gst_number = serializers.CharField(allow_null=True)
    pincode = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()


class AdminActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for admin activity logs."""
    
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    
    class Meta:
        model = AdminActivityLog
        fields = [
            'id', 'admin', 'admin_email', 'action', 'target_type',
            'target_id', 'description', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'admin', 'created_at']


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings."""
    
    typed_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = [
            'id', 'key', 'value', 'typed_value', 'setting_type',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_typed_value(self, obj):
        return obj.get_typed_value()


class SystemSettingsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating system settings."""
    
    class Meta:
        model = SystemSettings
        fields = ['value']


class PincodeMappingSerializer(serializers.ModelSerializer):
    """Serializer for pincode mappings."""
    
    assigned_admin_email = serializers.EmailField(
        source='assigned_admin.email',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = PincodeMapping
        fields = [
            'id', 'pincode', 'region_name', 'state', 'district',
            'assigned_admin', 'assigned_admin_email', 'assigned_franchise',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FilingReportSerializer(serializers.Serializer):
    """Serializer for filing reports."""
    
    filing_type = serializers.CharField()
    total_count = serializers.IntegerField()
    filed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    nil_count = serializers.IntegerField()
    total_taxable_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=15, decimal_places=2)


class PaymentReportSerializer(serializers.Serializer):
    """Serializer for payment reports."""
    
    total_invoiced = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    collection_rate = serializers.FloatField()
