from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import RateSlab, ProformaInvoice, Invoice, PaymentRecord

@admin.register(RateSlab)
class RateSlabAdmin(ModelAdmin):
    list_display = ('name', 'min_invoices', 'max_invoices', 'price', 'is_active', 'effective_from')
    list_filter = ('is_active',)

@admin.register(ProformaInvoice)
class ProformaInvoiceAdmin(ModelAdmin):
    list_display = ('invoice_number', 'user', 'total_amount', 'status', 'valid_until', 'created_at')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'user__email')

@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('invoice_number', 'user', 'total_amount', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('invoice_number', 'user__email', 'payment_reference')

@admin.register(PaymentRecord)
class PaymentRecordAdmin(ModelAdmin):
    list_display = ('id', 'user', 'amount', 'gateway', 'status', 'created_at')
    list_filter = ('gateway', 'status')
    search_fields = ('user__email', 'gateway_payment_id')
