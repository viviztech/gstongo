from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet, GeneratedReportViewSet, ScheduledReportViewSet,
    DashboardViewSet, AuditLogViewSet, APIKeyViewSet, WebhookViewSet
)

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='report-templates')
router.register(r'reports', GeneratedReportViewSet, basename='generated-reports')
router.register(r'schedules', ScheduledReportViewSet, basename='scheduled-reports')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')
router.register(r'api-keys', APIKeyViewSet, basename='api-keys')
router.register(r'webhooks', WebhookViewSet, basename='webhooks')

urlpatterns = [
    path('', include(router.urls)),
]
