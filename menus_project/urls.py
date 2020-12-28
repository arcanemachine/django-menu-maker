from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

import server_config

from . import views
from api.views import verify_email_view as api_views_verify_email_view

urlpatterns = [
    path('', views.root, name='root'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/rest-auth/registration/account-confirm-email/<key>/',
        api_views_verify_email_view, name='verify_email_view'),
    path('api/v1/rest-auth/', include('dj_rest_auth.urls')),
    path('api/v1/rest-auth/registration/',
         include('dj_rest_auth.registration.urls')),
    path('api/v1/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('captcha/', include('captcha.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('restaurants/<slug:restaurant_slug>/menus/', include('menus.urls')),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
]

if server_config.SERVER_NAME == 'dev':
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
