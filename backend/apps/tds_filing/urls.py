from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TDSReturnViewSet

router = DefaultRouter()
router.register(r'returns', TDSReturnViewSet, basename='tds-returns')

urlpatterns = [
    path('', include(router.urls)),
]
