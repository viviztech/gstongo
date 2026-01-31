from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Enquiry, SupportTicket, TicketComment, JobTicket, JobTask, KnowledgeBase


@admin.register(Enquiry)
class EnquiryAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'service_interest', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'service_interest', 'source', 'state')
    search_fields = ('name', 'email', 'phone', 'message')
    date_hierarchy = 'created_at'


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0


@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    list_display = ('ticket_number', 'customer', 'subject', 'category', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'sla_breached')
    search_fields = ('ticket_number', 'subject', 'customer__email')
    date_hierarchy = 'created_at'
    inlines = [TicketCommentInline]


class JobTaskInline(admin.TabularInline):
    model = JobTask
    extra = 0


@admin.register(JobTicket)
class JobTicketAdmin(ModelAdmin):
    list_display = ('job_number', 'customer', 'title', 'job_type', 'priority', 'status', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'job_type', 'team')
    search_fields = ('job_number', 'title', 'customer__email')
    date_hierarchy = 'created_at'
    inlines = [JobTaskInline]


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_featured', 'views', 'helpful_votes')
    list_filter = ('category', 'is_published', 'is_featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
