"""

django.contrib.auth views:
    accounts/ register/ [name='register']
    accounts/ login/ [name='login']
    accounts/ logout/ [name='logout']
    accounts/ password_change/ [name='password_change']
    accounts/ password_change/done/ [name='password_change_done']
    accounts/ password_reset/ [name='password_reset']
    accounts/ password_reset/done/ [name='password_reset_done']
    accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
    accounts/ reset/done/ [name='password_reset_complete']

"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

import keys

from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('restaurant/', include('restaurants.urls')),
    path('restaurant/<slug:restaurant_slug>/menu/', include('menus.urls')),
]

if keys.SERVER_NAME == 'dev':
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
