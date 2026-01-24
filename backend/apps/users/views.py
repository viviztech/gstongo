"""
Views for User authentication and profile management.
"""
import random
import pyotp
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from twilio.rest import Client
import firebase_admin
from firebase_admin import messaging

from .models import User, UserProfile, AdminProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, OTPVerificationSerializer, OTPSendSerializer,
    AdminProfileSerializer, ChangePasswordSerializer
)


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_email_otp(user, otp):
    """Send OTP via email."""
    subject = 'Your GSTONGO Verification Code'
    message = f'Your verification code is: {otp}\n\nThis code will expire in 5 minutes.'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_sms_otp(user, otp):
    """Send OTP via SMS using Twilio."""
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f'Your GSTONGO verification code is: {otp}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        return message.sid
    return None


def send_push_notification(user, title, body):
    """Send push notification via Firebase."""
    if user.profile.fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=user.profile.fcm_token,
        )
        messaging.send(message)


class UserRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class OTPViewSet(viewsets.ViewSet):
    """ViewSet for OTP operations."""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Send OTP to user."""
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = request.data.get('email')
        phone = request.data.get('phone')
        method = serializer.validated_data['method']
        
        if method == 'email':
            if not email:
                return Response(
                    {'error': 'Email is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            otp = generate_otp()
            user.email_otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_email_otp(user, otp)
            
        elif method == 'phone':
            if not phone:
                return Response(
                    {'error': 'Phone number is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                user = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            otp = generate_otp()
            user.phone_otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_sms_otp(user, otp)
        
        return Response({
            'message': f'OTP sent successfully via {method}.'
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify OTP."""
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = request.data.get('email')
        phone = request.data.get('phone')
        otp = serializer.validated_data['otp']
        method = serializer.validated_data['method']
        
        if method == 'email':
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            try:
                user = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if user.verify_otp(otp, method):
            if method == 'email':
                user.email_verified = True
                user.email_otp = None
            else:
                user.phone_verified = True
                user.phone_otp = None
            user.save()
            return Response({
                'message': 'OTP verified successfully.',
                'verified': True
            })
        else:
            return Response(
                {'error': 'Invalid or expired OTP.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get user profile."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(profile).data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with additional user data."""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.last_login_at = timezone.now()
            user.save()
            
            # Include user data in response
            response.data['user'] = UserSerializer(user).data
            response.data['profile'] = UserProfileSerializer(
                user.profile, context={'request': request}
            ).data
        return response


class ChangePasswordView(viewsets.ViewSet):
    """View for changing password."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Invalidate existing tokens
        RefreshToken.for_user(user)
        
        return Response({
            'message': 'Password changed successfully.'
        })


class AdminProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for admin profile."""
    
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'admin_profile'):
            return AdminProfile.objects.filter(user=self.request.user)
        return AdminProfile.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'You are not an admin user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)


class UserManagementViewSet(viewsets.ModelViewSet):
    """ViewSet for admin user management."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return User.objects.none()
        return User.objects.all()
    
    def list(self, request, *args, **kwargs):
        """List all users."""
        queryset = self.get_queryset()
        # Filter by various parameters
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated.'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': 'User activated.'})
