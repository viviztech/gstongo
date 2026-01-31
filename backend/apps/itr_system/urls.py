"""
URL patterns for ITR Filing app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ITRFilingViewSet

router = DefaultRouter()
router.register(r'filings', ITRFilingViewSet, basename='itr-filings')

urlpatterns = [
    path('', include(router.urls)),
]
