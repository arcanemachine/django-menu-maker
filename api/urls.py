from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'api'

urlpatterns = [
    path('',
         views.api_root,
         name='api_root'),
    path('api-token-auth/',
         obtain_auth_token,
         name='api_token_auth'),

    # users
    path('users/is-username-available/<str:username>/',
         views.is_username_available,
         name='is_username_available'),

    # restaurants
    path('restaurants/',
         views.RestaurantList.as_view(),
         name='restaurant_list'),
    path('restaurants/<int:restaurant_pk>/',
         views.RestaurantDetail.as_view(),
         name='restaurant_detail'),
    path('restaurants/<int:restaurant_pk>/menus/',
         views.MenuList.as_view(),
         name='menu_list'),
    path('restaurants/<int:restaurant_pk>/menus/<int:menu_pk>/',
         views.MenuDetail.as_view(),
         name='menu_detail'),
    path('restaurants/<int:restaurant_pk>/menus/<int:menu_pk>/sections/',
         views.MenuSectionList.as_view(),
         name='menusection_list'),
    path('restaurants/<int:restaurant_pk>/menus/<int:menu_pk>/sections/'
         '<int:menusection_pk>/',
         views.MenuSectionDetail.as_view(),
         name='menusection_detail'),
    path('restaurants/<int:restaurant_pk>/menus/<int:menu_pk>/sections/'
         '<int:menusection_pk>/items/',
         views.MenuItemList.as_view(),
         name='menuitem_list'),
    path('restaurants/<int:restaurant_pk>/menus/<int:menu_pk>/sections/'
         '<int:menusection_pk>/items/<int:menuitem_pk>/',
         views.MenuItemDetail.as_view(),
         name='menuitem_detail'),
    ]
