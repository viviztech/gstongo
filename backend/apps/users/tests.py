"""
Unit tests for User app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from apps.users.models import User, UserProfile


class UserModelTests(TestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a user with email."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_email_is_normalized(self):
        """Test that email is normalized."""
        email = 'Test@EXAMPLE.COM'
        user = User.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'Test@example.com')
    
    def test_user_cin_generation(self):
        """Test that CIN is generated on profile creation."""
        user = User.objects.create_user(
            email='cin_test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        profile = UserProfile.objects.get(user=user)
        
        self.assertIsNotNone(profile.cin)
        self.assertTrue(profile.cin.startswith('CIN-'))
    
    def test_user_str_representation(self):
        """Test user string representation."""
        email = 'str_test@example.com'
        user = User.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), email)


class UserAPITests(APITestCase):
    """Test cases for User API endpoints."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='api_test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.get(user=self.user)
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('auth-register-list')
        data = {
            'email': 'new_user@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+919876543210'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], data['email'])
    
    def test_user_login(self):
        """Test user login endpoint."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'api_test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'api_test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_profile_authenticated(self):
        """Test getting user profile when authenticated."""
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cin'], self.profile.cin)
    
    def test_get_user_profile_unauthenticated(self):
        """Test that unauthenticated users cannot access profile."""
        url = reverse('profile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password(self):
        """Test password change endpoint."""
        self.client.force_authenticate(user=self.user)
        url = reverse('password_change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))


class UserProfileTests(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='profile_test@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='Test'
        )
    
    def test_profile_creation(self):
        """Test that profile is created when user is created."""
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertTrue(profile.cin.startswith('CIN-'))
    
    def test_full_address(self):
        """Test getting full address."""
        profile = UserProfile.objects.get(user=self.user)
        profile.address_line_1 = '123 Test Street'
        profile.city = 'Test City'
        profile.state = 'Test State'
        profile.pincode = '123456'
        profile.save()
        
        full_address = profile.get_full_address()
        self.assertIn('123 Test Street', full_address)
        self.assertIn('Test City', full_address)
    
    def test_gst_number_validation(self):
        """Test GST number validation."""
        profile = UserProfile.objects.get(user=self.user)
        profile.gst_number = '27ABCDE1234F1Z5'
        profile.save()
        
        self.assertEqual(profile.gst_state_code, '27')  # State code from GST number
    
    def test_pincode_validation(self):
        """Test pincode format validation."""
        profile = UserProfile.objects.get(user=self.user)
        profile.pincode = '123456'
        profile.save()
        
        self.assertEqual(len(profile.pincode), 6)
        self.assertTrue(profile.pincode.isdigit())
