from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationSchedule, FCMToken

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'category', 'is_active')
    list_filter = ('template_type', 'category', 'is_active')
    search_fields = ('name', 'subject')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'category', 'status', 'created_at')
    list_filter = ('channel', 'category', 'status')
    search_fields = ('user__email', 'title', 'message')
    date_hierarchy = 'created_at'

@admin.register(NotificationSchedule)
class NotificationScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'schedule_type', 'trigger_type', 'is_active', 'next_run_at')
    list_filter = ('schedule_type', 'trigger_type', 'is_active')

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__email', 'token')
