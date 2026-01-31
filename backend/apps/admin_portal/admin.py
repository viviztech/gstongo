from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AdminDashboardStats, UserSearchHistory, AdminActivityLog, SystemSettings, PincodeMapping

@admin.register(AdminDashboardStats)
class AdminDashboardStatsAdmin(ModelAdmin):
    list_display = ('date', 'total_users', 'new_users', 'payments_collected')
    date_hierarchy = 'date'

@admin.register(UserSearchHistory)
class UserSearchHistoryAdmin(ModelAdmin):
    list_display = ('admin', 'search_type', 'search_value', 'result_count', 'searched_at')
    list_filter = ('search_type',)
    search_fields = ('admin__email', 'search_value')

@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'created_at')
    list_filter = ('action', 'target_type')
    search_fields = ('admin__email', 'description')
    date_hierarchy = 'created_at'

@admin.register(SystemSettings)
class SystemSettingsAdmin(ModelAdmin):
    list_display = ('key', 'value', 'setting_type')
    search_fields = ('key', 'description')

@admin.register(PincodeMapping)
class PincodeMappingAdmin(ModelAdmin):
    list_display = ('pincode', 'region_name', 'state', 'district', 'is_active')
    list_filter = ('state', 'is_active')
    search_fields = ('pincode', 'region_name', 'district')
