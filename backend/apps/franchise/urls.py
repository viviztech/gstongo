from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FranchiseViewSet, PincodeMappingViewSet, CustomerAssignmentViewSet

router = DefaultRouter()
router.register(r'franchises', FranchiseViewSet, basename='franchises')
router.register(r'pincodes', PincodeMappingViewSet, basename='pincodes')
router.register(r'assignments', CustomerAssignmentViewSet, basename='assignments')

urlpatterns = [
    path('', include(router.urls)),
]
