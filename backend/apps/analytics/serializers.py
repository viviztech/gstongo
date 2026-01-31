"""
Serializers for Analytics and Reporting.
"""
from rest_framework import serializers
from .models import (
    ReportTemplate, GeneratedReport, ScheduledReport,
    DashboardWidget, UserDashboard, AuditLog, APIKey, Webhook
)


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'query_config',
            'columns', 'filters', 'default_format', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GeneratedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'template', 'template_name', 'name', 'report_type', 'format',
            'parameters', 'status', 'file', 'file_size', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'file', 'file_size', 'error_message', 'started_at', 'completed_at', 'created_at']


class ScheduledReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'template', 'template_name', 'name', 'frequency',
            'day_of_week', 'day_of_month', 'time', 'recipients',
            'is_active', 'last_run', 'next_run', 'created_at'
        ]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'data_source', 'query_config',
            'display_config', 'position_x', 'position_y', 'width', 'height',
            'is_public', 'created_at'
        ]


class UserDashboardSerializer(serializers.ModelSerializer):
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserDashboard
        fields = ['id', 'name', 'widgets', 'layout', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'resource_type',
            'resource_id', 'details', 'ip_address', 'timestamp'
        ]


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_prefix', 'permissions', 'rate_limit',
            'is_active', 'last_used', 'request_count', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'key_prefix', 'last_used', 'request_count', 'created_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['name', 'permissions', 'rate_limit', 'expires_at']
    
    def create(self, validated_data):
        import secrets
        key = secrets.token_hex(32)
        validated_data['user'] = self.context['request'].user
        validated_data['key'] = key
        validated_data['key_prefix'] = key[:8]
        instance = super().create(validated_data)
        # Return the full key only on creation
        instance._full_key = key
        return instance


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'is_active',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery', 'last_response_code', 'created_at'
        ]
        read_only_fields = ['id', 'total_deliveries', 'successful_deliveries', 'failed_deliveries', 'last_delivery', 'last_response_code', 'created_at']


class WebhookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['name', 'url', 'events']
    
    def create(self, validated_data):
        import secrets
        validated_data['user'] = self.context['request'].user
        validated_data['secret'] = secrets.token_hex(32)
        return super().create(validated_data)
