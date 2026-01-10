"""
URL patterns for GST Filing app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GSTFilingViewSet, InvoiceViewSet, FilingAdminViewSet

router = DefaultRouter()
router.register(r'filings', GSTFilingViewSet, basename='gst-filings')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'admin', FilingAdminViewSet, basename='filing-admin')

urlpatterns = [
    path('', include(router.urls)),
]
