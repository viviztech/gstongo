"""
Serializers for Support & Ticketing.
"""
from rest_framework import serializers
from .models import Enquiry, SupportTicket, TicketComment, JobTicket, JobTask, KnowledgeBase


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = [
            'id', 'name', 'email', 'phone', 'city', 'state', 'pincode',
            'service_interest', 'message', 'status', 'assigned_to',
            'follow_up_date', 'notes', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'assigned_to', 'created_at']


class EnquiryCreateSerializer(serializers.ModelSerializer):
    """For public enquiry form - no auth required."""
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'city', 'state', 'pincode', 'service_interest', 'message', 'source']


class TicketCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = ['id', 'author', 'author_name', 'author_email', 'message', 'is_internal', 'attachment', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'customer', 'customer_email',
            'subject', 'description', 'category', 'priority', 'status',
            'assigned_to', 'assigned_to_email', 'sla_due', 'sla_breached',
            'resolved_at', 'resolution_notes', 'rating', 'feedback',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ticket_number', 'customer', 'sla_breached', 'resolved_at', 'created_at', 'updated_at']


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'category', 'priority']
    
    def create(self, validated_data):
        import uuid
        validated_data['customer'] = self.context['request'].user
        validated_data['ticket_number'] = f"TKT{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class JobTaskSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    
    class Meta:
        model = JobTask
        fields = ['id', 'title', 'description', 'order', 'status', 'assigned_to', 'assigned_to_email', 'completed_at', 'notes']


class JobTicketSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    tasks = JobTaskSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = JobTicket
        fields = [
            'id', 'job_number', 'customer', 'customer_email',
            'title', 'description', 'job_type', 'assigned_to', 'assigned_to_email', 'team',
            'priority', 'status', 'due_date', 'started_at', 'completed_at',
            'estimated_hours', 'actual_hours', 'quality_score', 'reviewer_notes',
            'tasks', 'progress_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'job_number', 'customer', 'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        total_tasks = obj.tasks.count()
        if total_tasks == 0:
            return 0
        completed = obj.tasks.filter(status='completed').count()
        return int((completed / total_tasks) * 100)


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'slug', 'category', 'question', 'content', 'is_featured', 'views', 'helpful_votes']
