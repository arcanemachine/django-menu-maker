from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('',
         views.RestaurantList.as_view(),
         name='restaurant_list'),
    path('<int:restaurant_pk>/',
         views.RestaurantDetail.as_view(),
         name='restaurant_detail'),
    path('<int:restaurant_pk>/m/',
         views.MenuList.as_view(),
         name='menu_list'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/',
         views.MenuDetail.as_view(),
         name='menu_detail'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/',
         views.MenuSectionList.as_view(),
         name='menusection_list'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/',
         views.MenuSectionDetail.as_view(),
         name='menusection_detail'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/',
         views.MenuItemList.as_view(),
         name='menuitem_list'),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/'
         '<int:menuitem_pk>/',
         views.MenuItemDetail.as_view(),
         name='menuitem_detail'),
    ]
