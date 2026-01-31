from django.contrib import admin
from .models import AdminDashboardStats, UserSearchHistory, AdminActivityLog, SystemSettings, PincodeMapping

@admin.register(AdminDashboardStats)
class AdminDashboardStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'new_users', 'payments_collected')
    date_hierarchy = 'date'

@admin.register(UserSearchHistory)
class UserSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('admin', 'search_type', 'search_value', 'result_count', 'searched_at')
    list_filter = ('search_type',)
    search_fields = ('admin__email', 'search_value')

@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'created_at')
    list_filter = ('action', 'target_type')
    search_fields = ('admin__email', 'description')
    date_hierarchy = 'created_at'

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'setting_type')
    search_fields = ('key', 'description')

@admin.register(PincodeMapping)
class PincodeMappingAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'region_name', 'state', 'district', 'is_active')
    list_filter = ('state', 'is_active')
    search_fields = ('pincode', 'region_name', 'district')
