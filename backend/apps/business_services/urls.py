from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceApplicationViewSet

router = DefaultRouter()
router.register(r'applications', ServiceApplicationViewSet, basename='service-applications')

urlpatterns = [
    path('', include(router.urls)),
]
