from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Franchise, FranchiseTerritory, FranchiseCommission, PincodeMapping, CustomerAssignment


class FranchiseTerritoryInline(admin.TabularInline):
    model = FranchiseTerritory
    extra = 0


class FranchiseCommissionInline(admin.TabularInline):
    model = FranchiseCommission
    extra = 0


@admin.register(Franchise)
class FranchiseAdmin(ModelAdmin):
    list_display = ('franchise_code', 'business_name', 'city', 'state', 'status', 'total_customers', 'total_revenue', 'rating')
    list_filter = ('status', 'franchise_type', 'state', 'kyc_verified')
    search_fields = ('franchise_code', 'business_name', 'contact_email', 'pan_number')
    date_hierarchy = 'created_at'
    inlines = [FranchiseTerritoryInline, FranchiseCommissionInline]


@admin.register(FranchiseTerritory)
class FranchiseTerritoryAdmin(ModelAdmin):
    list_display = ('franchise', 'state', 'district', 'pincode_start', 'pincode_end', 'is_exclusive', 'is_active')
    list_filter = ('state', 'is_exclusive', 'is_active')


@admin.register(FranchiseCommission)
class FranchiseCommissionAdmin(ModelAdmin):
    list_display = ('franchise', 'month', 'year', 'gross_revenue', 'commission_amount', 'net_payable', 'status')
    list_filter = ('status', 'year', 'month')
    search_fields = ('franchise__franchise_code', 'franchise__business_name')


@admin.register(PincodeMapping)
class PincodeMappingAdmin(ModelAdmin):
    list_display = ('pincode', 'franchise', 'district', 'state', 'is_active', 'priority')
    list_filter = ('state', 'is_active')
    search_fields = ('pincode', 'district', 'franchise__business_name')


@admin.register(CustomerAssignment)
class CustomerAssignmentAdmin(ModelAdmin):
    list_display = ('customer', 'franchise', 'assigned_by', 'assigned_at', 'is_active')
    list_filter = ('assigned_by', 'is_active')
    search_fields = ('customer__email', 'franchise__business_name')
