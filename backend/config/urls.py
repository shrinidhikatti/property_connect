from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/properties/', include('properties.urls')),
    path('api/v1/documents/', include('documents.urls')),
    path('api/v1/verifications/', include('verifications.urls')),
    path('api/v1/conversations/', include('conversations.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/payments/', include('payments.urls')),

    # JWT token refresh
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
