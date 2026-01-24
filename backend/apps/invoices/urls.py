"""
URL patterns for Invoices app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RateSlabViewSet, ProformaInvoiceViewSet, InvoiceViewSet, PaymentViewSet, AdminPaymentViewSet

router = DefaultRouter()
router.register(r'rate-slabs', RateSlabViewSet, basename='rate-slabs')
router.register(r'proforma', ProformaInvoiceViewSet, basename='proforma')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'admin', AdminPaymentViewSet, basename='admin-payments')

urlpatterns = [
    path('', include(router.urls)),
]
