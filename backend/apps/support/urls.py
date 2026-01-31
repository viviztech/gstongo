from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnquiryViewSet, SupportTicketViewSet, JobTicketViewSet, KnowledgeBaseViewSet

router = DefaultRouter()
router.register(r'enquiries', EnquiryViewSet, basename='enquiries')
router.register(r'tickets', SupportTicketViewSet, basename='support-tickets')
router.register(r'jobs', JobTicketViewSet, basename='job-tickets')
router.register(r'kb', KnowledgeBaseViewSet, basename='knowledge-base')

urlpatterns = [
    path('', include(router.urls)),
]
