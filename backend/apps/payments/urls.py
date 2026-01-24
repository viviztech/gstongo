"""
URL patterns for Payments app.
"""
from django.urls import path
from .views import (
    PaymentInitView,
    PaymentVerifyView,
    PaymentWebhookView,
    payment_history,
    payment_detail,
)

urlpatterns = [
    # Payment initialization and verification
    path('init/', PaymentInitView.as_view(), name='payment-init'),
    path('verify/', PaymentVerifyView.as_view(), name='payment-verify'),
    
    # Webhook handler
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    
    # Payment history and details
    path('history/', payment_history, name='payment-history'),
    path('<int:transaction_id>/', payment_detail, name='payment-detail'),
]
