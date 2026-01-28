"""
URL patterns for User app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationViewSet, OTPViewSet, UserProfileViewSet,
    CustomTokenObtainPairView, ChangePasswordView, AdminProfileViewSet,
    UserManagementViewSet, PasswordResetViewSet
)

router = DefaultRouter()
router.register(r'register', UserRegistrationViewSet, basename='auth-register')
router.register(r'otp', OTPViewSet, basename='auth-otp')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'admin', AdminProfileViewSet, basename='admin-profile')
router.register(r'manage', UserManagementViewSet, basename='user-manage')
router.register(r'password', PasswordResetViewSet, basename='auth-password')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/change/', ChangePasswordView.as_view({'post': 'create'}), name='password_change'),
]
