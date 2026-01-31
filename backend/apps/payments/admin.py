from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'gateway', 'status', 'created_at')
    list_filter = ('gateway', 'status')
    search_fields = ('user__email', 'gateway_order_id', 'gateway_payment_id')
    date_hierarchy = 'created_at'
