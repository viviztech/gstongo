"""
User models for GSTONGO project.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for GSTONGO."""
    
    username = None  # Disable username, use email instead
    email = models.EmailField('email address', unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?[1-9]\d{1,14}$')],
        unique=True,
        null=True,
        blank=True
    )
    
    # OTP Verification fields
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def generate_cin(self):
        """Generate unique Customer Identification Number."""
        return f"CIN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    def verify_otp(self, otp, method='email'):
        """Verify OTP for email or phone."""
        if method == 'email':
            return self.email_otp == otp and self.is_otp_valid()
        elif method == 'phone':
            return self.phone_otp == otp and self.is_otp_valid()
        return False
    
    def is_otp_valid(self):
        """Check if OTP is still valid (5 minutes window)."""
        if self.otp_created_at:
            elapsed = timezone.now() - self.otp_created_at
            return elapsed.total_seconds() < 300  # 5 minutes
        return False


class UserProfile(models.Model):
    """Extended user profile for customers."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Customer Identification Number
    cin = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    
    # GST Details
    gst_number = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(15)],
        null=True,
        blank=True
    )
    gst_state_code = models.CharField(max_length=2, null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    trade_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Address Details
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    
    # Business Details
    business_type = models.CharField(max_length=50, null=True, blank=True)
    registration_type = models.CharField(max_length=50, null=True, blank=True)
    date_of_registration = models.DateField(null=True, blank=True)
    
    # Preferences
    preferred_notification_channel = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('whatsapp', 'WhatsApp'),
            ('push', 'Push Notification'),
        ],
        default='email'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.cin:
            self.cin = self.user.generate_cin()
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Return full address as string."""
        parts = [self.address_line_1, self.address_line_2, self.city, self.state, self.pincode]
        return ', '.join([p for p in parts if p])
    
    def validate_gst_number(self):
        """Basic GST number validation."""
        if self.gst_number and len(self.gst_number) == 15:
            # Extract state code from GST number
            self.gst_state_code = self.gst_number[:2]
            return True
        return False


class AdminProfile(models.Model):
    """Admin user profile with additional permissions."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    
    # Admin details
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    
    # Permissions
    can_manage_users = models.BooleanField(default=False)
    can_manage_rate_slabs = models.BooleanField(default=False)
    can_manage_filings = models.BooleanField(default=False)
    can_manage_payments = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_send_notifications = models.BooleanField(default=False)
    can_manage_admins = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_profiles'
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f"Admin: {self.user.email}"
