"""
Serializers for User models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, AdminProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'email_verified', 'phone_verified', 'two_factor_enabled',
            'created_at', 'updated_at', 'last_login_at'
        ]
        read_only_fields = ['id', 'email_verified', 'phone_verified', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'cin', 'gst_number', 'gst_state_code', 'legal_name', 'trade_name',
            'address_line_1', 'address_line_2', 'pincode', 'city', 'state',
            'business_type', 'registration_type', 'date_of_registration',
            'preferred_notification_channel', 'email', 'first_name', 'last_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['cin', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'gst_number', 'legal_name', 'trade_name',
            'address_line_1', 'address_line_2', 'pincode', 'city', 'state',
            'business_type', 'registration_type', 'date_of_registration',
            'preferred_notification_channel', 'first_name', 'last_name', 'phone_number'
        ]
    
    def validate_gst_number(self, value):
        """Validate GST number format."""
        if value and len(value) != 15:
            raise serializers.ValidationError('GST number must be 15 characters.')
        return value
    
    def validate_pincode(self, value):
        """Validate pincode format (India)."""
        if value and (len(value) != 6 or not value.isdigit()):
            raise serializers.ValidationError('Pincode must be 6 digits.')
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        return super().update(instance, validated_data)


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    otp = serializers.CharField(max_length=6, required=True)
    method = serializers.ChoiceField(
        choices=['email', 'phone'],
        default='email'
    )


class OTPSendSerializer(serializers.Serializer):
    """Serializer for requesting OTP."""
    
    method = serializers.ChoiceField(
        choices=['email', 'phone'],
        default='email'
    )


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for AdminProfile model."""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = [
            'employee_id', 'department', 'designation',
            'can_manage_users', 'can_manage_rate_slabs', 'can_manage_filings',
            'can_manage_payments', 'can_view_reports', 'can_send_notifications',
            'can_manage_admins', 'email', 'first_name', 'last_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists with this email."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if user exists or not
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return attrs


class PasswordResetVerifySerializer(serializers.Serializer):
    """Serializer for verifying password reset token."""
    
    token = serializers.CharField(required=True)
