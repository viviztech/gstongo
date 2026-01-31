"""
Serializers for Document Vault.
"""
from rest_framework import serializers
from .models import Document, DocumentCategory, DocumentShare, OrderTracking, OrderMilestone


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description', 'icon']


class DocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'category', 'category_name', 'name', 'description', 'file',
            'file_type', 'file_size', 'status', 'expiry_date', 'tags',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_type', 'file_size', 'uploaded_at', 'updated_at']


class DocumentShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentShare
        fields = ['id', 'share_token', 'shared_with_email', 'expires_at', 'is_active', 'access_count', 'created_at']
        read_only_fields = ['id', 'share_token', 'access_count', 'created_at']


class OrderMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMilestone
        fields = ['id', 'step_number', 'title', 'description', 'is_completed', 'completed_at']


class OrderTrackingSerializer(serializers.ModelSerializer):
    milestones = OrderMilestoneSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderTracking
        fields = [
            'id', 'order_reference', 'service_type', 'service_name', 'status',
            'current_step', 'total_steps', 'progress_percentage', 'amount', 'payment_status',
            'estimated_completion', 'completed_at', 'milestones', 'created_at', 'updated_at'
        ]
    
    def get_progress_percentage(self, obj):
        if obj.total_steps == 0:
            return 0
        return int((obj.current_step / obj.total_steps) * 100)
