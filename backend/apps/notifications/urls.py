"""
URL patterns for Notifications app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationTemplateViewSet, NotificationViewSet,
    NotificationSendViewSet, NotificationScheduleViewSet, FCMTokenViewSet
)

router = DefaultRouter()
router.register(r'templates', NotificationTemplateViewSet, basename='notification-templates')
router.register(r'list', NotificationViewSet, basename='notifications')
router.register(r'send', NotificationSendViewSet, basename='send-notifications')
router.register(r'schedules', NotificationScheduleViewSet, basename='notification-schedules')
router.register(r'fcm', FCMTokenViewSet, basename='fcm-tokens')

urlpatterns = [
    path('', include(router.urls)),
]
