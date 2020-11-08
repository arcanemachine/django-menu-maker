from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('',
         views.RestaurantList.as_view(),
         name='restaurant_list_create'),
    path('<pk>/',
         views.RestaurantDetail.as_view(),
         name='restaurant_retrieve_update_destroy'),
    path('<int:restaurant_pk>/m/',
         views.MenuList.as_view(),
         name='menu_list_create'),
    path('<int:restaurant_pk>/m/<pk>/',
         views.MenuDetail.as_view(),
         name='menu_retrieve_update_destroy'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/',
         views.MenuSectionList.as_view(),
         name='menusection_list_create'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<pk>/',
         views.MenuSectionDetail.as_view(),
         name='menusection_retrieve_update_destroy'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/',
         views.MenuItemList.as_view(),
         name='menuitem_list_create'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/<pk>/',
         views.MenuItemDetail.as_view(),
         name='menuitem_retrieve_update_destroy'),
    ]
