"""
URL configuration for GSTONGO project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/core/', include('apps.core.urls')),
    path('api/v1/gst/', include('apps.gst_filing.urls')),
    path('api/v1/itr/', include('apps.itr_system.urls')),
    path('api/v1/tds/', include('apps.tds_filing.urls')),
    path('api/v1/services/', include('apps.business_services.urls')),
    path('api/v1/vault/', include('apps.document_vault.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/invoices/', include('apps.invoices.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/admin/', include('apps.admin_portal.urls')),
    
    # Swagger/OpenAPI Documentation
    # path('api-docs/', include('drf_yasg.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
