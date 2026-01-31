from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, AdminProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    # Custom fields for our User model
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Verification Info', {'fields': ('phone_number', 'email_verified', 'phone_verified')}),
        ('Two-Factor Auth', {'fields': ('two_factor_enabled',)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Verification Info', {'fields': ('phone_number',)}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cin', 'gst_number', 'legal_name', 'city', 'state')
    search_fields = ('user__email', 'cin', 'gst_number', 'legal_name')
    list_filter = ('business_type', 'registration_type', 'state')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'designation')
    search_fields = ('user__email', 'employee_id')
    list_filter = ('department', 'designation')
