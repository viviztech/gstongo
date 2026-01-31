from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TDSReturn, TDSDeductee, TDSChallan


class TDSDeducteeInline(admin.TabularInline):
    model = TDSDeductee
    extra = 0


class TDSChallanInline(admin.TabularInline):
    model = TDSChallan
    extra = 0


@admin.register(TDSReturn)
class TDSReturnAdmin(ModelAdmin):
    list_display = ('user', 'return_type', 'financial_year', 'quarter', 'status', 'total_deducted', 'created_at')
    list_filter = ('return_type', 'status', 'financial_year', 'quarter')
    search_fields = ('user__email', 'tan_number', 'acknowledgment_number')
    inlines = [TDSDeducteeInline, TDSChallanInline]


@admin.register(TDSDeductee)
class TDSDeducteeAdmin(ModelAdmin):
    list_display = ('tds_return', 'pan', 'name', 'tds_deducted', 'created_at')
    search_fields = ('pan', 'name')


@admin.register(TDSChallan)
class TDSChallanAdmin(ModelAdmin):
    list_display = ('tds_return', 'challan_number', 'amount', 'challan_date')
    search_fields = ('challan_number',)
