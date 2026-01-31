from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ITRFiling, ITR1Details, ITRDocument

class ITR1DetailsInline(admin.StackedInline):
    model = ITR1Details
    extra = 0

class ITRDocumentInline(admin.TabularInline):
    model = ITRDocument
    extra = 0

@admin.register(ITRFiling)
class ITRFilingAdmin(ModelAdmin):
    list_display = ('user', 'filing_type', 'financial_year', 'assessment_year', 'status', 'total_income', 'created_at')
    list_filter = ('filing_type', 'status', 'financial_year', 'assessment_year')
    search_fields = ('user__email', 'acknowledgment_number')
    date_hierarchy = 'created_at'
    inlines = [ITR1DetailsInline, ITRDocumentInline]

@admin.register(ITR1Details)
class ITR1DetailsAdmin(ModelAdmin):
    list_display = ('filing', 'salary_income', 'tax_payable', 'created_at')
    search_fields = ('filing__user__email',)

@admin.register(ITRDocument)
class ITRDocumentAdmin(ModelAdmin):
    list_display = ('filing', 'document_type', 'uploaded_at')
    list_filter = ('document_type',)
    search_fields = ('filing__user__email',)
