"""
Views for Notifications.
"""
import re
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from twilio.rest import Client
import firebase_admin
from firebase_admin import messaging
from django.utils import timezone

from .models import NotificationTemplate, Notification, NotificationSchedule, FCMToken
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer,
    NotificationScheduleSerializer
)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for notification template management."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return NotificationTemplate.objects.none()
        return NotificationTemplate.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create notification template (admin only)."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_send_notifications:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for user notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user."""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('read')
        if is_read is not None:
            if is_read.lower() == 'true':
                queryset = queryset.filter(status='read')
            else:
                queryset = queryset.exclude(status='read')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List notifications with unread count."""
        queryset = self.get_queryset()
        unread_count = queryset.exclude(status='read').count()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'message': 'Notification marked as read.',
            'notification': NotificationSerializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        Notification.objects.filter(
            user=request.user
        ).exclude(status='read').update(
            status='read',
            read_at=timezone.now()
        )
        
        return Response({'message': 'All notifications marked as read.'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count."""
        count = Notification.objects.filter(
            user=request.user
        ).exclude(status='read').count()
        
        return Response({'unread_count': count})


class NotificationSendViewSet(viewsets.ViewSet):
    """ViewSet for sending notifications."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return Notification.objects.none()
        return Notification.objects.all()
    
    @action(detail=False, methods=['post'])
    def send_email(self, request):
        """Send email notification."""
        user_id = request.data.get('user_id')
        subject = request.data.get('subject')
        message = request.data.get('message')
        
        if not all([user_id, subject, message]):
            return Response(
                {'error': 'user_id, subject, and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.users.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            channel='email',
            category='general',
            title=subject,
            message=message
        )
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
            return Response({
                'message': 'Email sent successfully.',
                'notification_id': notification.id
            })
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_sms(self, request):
        """Send SMS notification."""
        user_id = request.data.get('user_id')
        message = request.data.get('message')
        
        if not all([user_id, message]):
            return Response(
                {'error': 'user_id and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.users.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not user.phone_number:
            return Response(
                {'error': 'User has no phone number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            channel='sms',
            category='general',
            title='SMS',
            message=message
        )
        
        try:
            if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=user.phone_number
                )
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                
                return Response({
                    'message': 'SMS sent successfully.',
                    'notification_id': notification.id
                })
            else:
                raise Exception('Twilio not configured')
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return Response(
                {'error': f'Failed to send SMS: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_push(self, request):
        """Send push notification."""
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        message = request.data.get('message')
        
        if not all([user_id, title, message]):
            return Response(
                {'error': 'user_id, title, and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.users.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get user's FCM tokens
        tokens = FCMToken.objects.filter(user=user, is_active=True)
        if not tokens:
            return Response(
                {'error': 'User has no active push notification tokens.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            channel='push',
            category='general',
            title=title,
            message=message
        )
        
        try:
            # Send to all user's devices
            registration_tokens = [t.token for t in tokens]
            message_obj = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                tokens=registration_tokens,
            )
            response = messaging.send_each_for_multicast(message_obj)
            
            notification.status = 'sent' if response.success_count > 0 else 'failed'
            notification.sent_at = timezone.now()
            notification.save()
            
            return Response({
                'message': 'Push notifications sent.',
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'notification_id': notification.id
            })
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return Response(
                {'error': f'Failed to send push notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for notification schedule management."""
    
    serializer_class = NotificationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return NotificationSchedule.objects.none()
        return NotificationSchedule.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create notification schedule (admin only)."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_send_notifications:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


class FCMTokenViewSet(viewsets.ModelViewSet):
    """ViewSet for FCM token management."""
    
    serializer_class = None  # No serializer needed
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FCMToken.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register FCM token for push notifications."""
        token = request.data.get('token')
        device_type = request.data.get('device_type', 'android')
        
        if not token:
            return Response(
                {'error': 'token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token already exists
        existing = FCMToken.objects.filter(token=token).first()
        if existing:
            existing.user = request.user
            existing.is_active = True
            existing.save()
            return Response({'message': 'Token updated.'})
        
        # Create new token
        FCMToken.objects.create(
            user=request.user,
            token=token,
            device_type=device_type
        )
        
        return Response({'message': 'Token registered.'})
    
    @action(detail=False, methods=['post'])
    def unregister(self, request):
        """Unregister FCM token."""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        FCMToken.objects.filter(token=token).update(is_active=False)
        
        return Response({'message': 'Token unregistered.'})
