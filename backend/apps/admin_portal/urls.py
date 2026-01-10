"""
URL patterns for Admin Portal app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, UserSearchViewSet, AdminActivityViewSet, SystemSettingsViewSet, PincodeMappingViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'search', UserSearchViewSet, basename='user-search')
router.register(r'activity', AdminActivityViewSet, basename='admin-activity')
router.register(r'settings', SystemSettingsViewSet, basename='system-settings')
router.register(r'pincodes', PincodeMappingViewSet, basename='pincode-mapping')

urlpatterns = [
    path('', include(router.urls)),
]
