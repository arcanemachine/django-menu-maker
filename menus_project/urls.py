from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

import server_config

from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('admin/', admin.site.urls),
    path('api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('api/v1/dj-rest-auth/registration/',
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
