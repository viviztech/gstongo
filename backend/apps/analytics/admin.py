from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    ReportTemplate, GeneratedReport, ScheduledReport,
    DashboardWidget, UserDashboard, AuditLog, APIKey, Webhook
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(ModelAdmin):
    list_display = ('name', 'report_type', 'is_public', 'created_by', 'created_at')
    list_filter = ('report_type', 'is_public')
    search_fields = ('name', 'description')


@admin.register(GeneratedReport)
class GeneratedReportAdmin(ModelAdmin):
    list_display = ('name', 'report_type', 'format', 'status', 'requested_by', 'created_at')
    list_filter = ('status', 'report_type', 'format')
    search_fields = ('name', 'requested_by__email')
    date_hierarchy = 'created_at'


@admin.register(ScheduledReport)
class ScheduledReportAdmin(ModelAdmin):
    list_display = ('name', 'template', 'frequency', 'is_active', 'last_run', 'next_run')
    list_filter = ('frequency', 'is_active')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(ModelAdmin):
    list_display = ('name', 'widget_type', 'data_source', 'is_public', 'created_by')
    list_filter = ('widget_type', 'is_public')


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'ip_address', 'timestamp')
    list_filter = ('action', 'resource_type')
    search_fields = ('user__email', 'resource_id')
    date_hierarchy = 'timestamp'


@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    list_display = ('name', 'user', 'key_prefix', 'is_active', 'rate_limit', 'request_count', 'last_used')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email', 'key_prefix')


@admin.register(Webhook)
class WebhookAdmin(ModelAdmin):
    list_display = ('name', 'user', 'url', 'is_active', 'total_deliveries', 'successful_deliveries', 'last_delivery')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email', 'url')
