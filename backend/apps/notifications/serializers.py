"""
Serializers for Notifications.
"""
from rest_framework import serializers
from .models import NotificationTemplate, Notification, NotificationSchedule, FCMToken


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'channel', 'category', 'subject',
            'message_template', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'channel', 'category', 'title', 'message',
            'status', 'sent_at', 'read_at', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'sent_at', 'read_at', 'error_message',
            'created_at', 'updated_at'
        ]


class NotificationScheduleSerializer(serializers.ModelSerializer):
    """Serializer for notification schedules."""
    
    class Meta:
        model = NotificationSchedule
        fields = [
            'id', 'name', 'template', 'scheduled_at', 'recipients',
            'is_recurring', 'recurring_type', 'is_active',
            'sent_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sent_count', 'created_at', 'updated_at']
