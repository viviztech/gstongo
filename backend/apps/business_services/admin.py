from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    ServiceApplication, ServiceDocument, CompanyIncorporation,
    FSSAIRegistration, MSMERegistration, PANTANApplication
)


class ServiceDocumentInline(admin.TabularInline):
    model = ServiceDocument
    extra = 0


@admin.register(ServiceApplication)
class ServiceApplicationAdmin(ModelAdmin):
    list_display = ('application_reference', 'user', 'service_type', 'status', 'created_at')
    list_filter = ('service_type', 'status')
    search_fields = ('user__email', 'application_reference', 'certificate_number')
    date_hierarchy = 'created_at'
    inlines = [ServiceDocumentInline]


@admin.register(CompanyIncorporation)
class CompanyIncorporationAdmin(ModelAdmin):
    list_display = ('application', 'company_type', 'proposed_name_1', 'cin')
    search_fields = ('proposed_name_1', 'cin')


@admin.register(FSSAIRegistration)
class FSSAIRegistrationAdmin(ModelAdmin):
    list_display = ('application', 'license_type', 'business_name', 'fssai_license_number')
    list_filter = ('license_type',)


@admin.register(MSMERegistration)
class MSMERegistrationAdmin(ModelAdmin):
    list_display = ('application', 'enterprise_type', 'enterprise_name', 'udyam_number')
    list_filter = ('enterprise_type',)


@admin.register(PANTANApplication)
class PANTANApplicationAdmin(ModelAdmin):
    list_display = ('application', 'application_type', 'applicant_name', 'issued_pan', 'issued_tan')
    list_filter = ('application_type',)
