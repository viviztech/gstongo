from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Document, DocumentCategory, DocumentShare, OrderTracking, OrderMilestone


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ModelAdmin):
    list_display = ('name', 'icon')


class DocumentShareInline(admin.TabularInline):
    model = DocumentShare
    extra = 0


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ('name', 'user', 'category', 'file_type', 'status', 'expiry_date', 'uploaded_at')
    list_filter = ('status', 'category', 'file_type')
    search_fields = ('name', 'user__email', 'description')
    date_hierarchy = 'uploaded_at'
    inlines = [DocumentShareInline]


class OrderMilestoneInline(admin.TabularInline):
    model = OrderMilestone
    extra = 0


@admin.register(OrderTracking)
class OrderTrackingAdmin(ModelAdmin):
    list_display = ('order_reference', 'user', 'service_type', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'service_type', 'payment_status')
    search_fields = ('order_reference', 'user__email', 'service_name')
    date_hierarchy = 'created_at'
    inlines = [OrderMilestoneInline]
