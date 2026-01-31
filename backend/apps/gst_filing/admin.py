from django.contrib import admin
from .models import GSTFiling, GSTR1Details, GSTR3BDetails, GSTR9BDetails, Invoice, FilingDocument

@admin.register(GSTFiling)
class GSTFilingAdmin(admin.ModelAdmin):
    list_display = ('user', 'filing_type', 'financial_year', 'month', 'status', 'created_at')
    list_filter = ('filing_type', 'status', 'financial_year', 'month')
    search_fields = ('user__email', 'filing_reference_number')
    date_hierarchy = 'created_at'

@admin.register(GSTR1Details)
class GSTR1DetailsAdmin(admin.ModelAdmin):
    list_display = ('filing', 'b2b_invoices_count', 'b2b_invoices_value', 'created_at')

@admin.register(GSTR3BDetails)
class GSTR3BDetailsAdmin(admin.ModelAdmin):
    list_display = ('filing', 'outward_taxable_supplies', 'total_credit', 'created_at')

@admin.register(GSTR9BDetails)
class GSTR9BDetailsAdmin(admin.ModelAdmin):
    list_display = ('filing', 'total_outward_supplies', 'auditor_name', 'created_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'filing', 'invoice_type', 'taxable_value', 'total_tax', 'invoice_date')
    list_filter = ('invoice_type',)
    search_fields = ('invoice_number', 'counterparty_name', 'counterparty_gstin')

@admin.register(FilingDocument)
class FilingDocumentAdmin(admin.ModelAdmin):
    list_display = ('filing', 'document_type', 'uploaded_at')
    list_filter = ('document_type',)
