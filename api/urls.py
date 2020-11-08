from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('',
         views.RestaurantList.as_view()),
    path('<pk>/',
         views.RestaurantDetail.as_view()),
    path('<int:restaurant_pk>/menus/',
         views.MenuList.as_view()),
    path('<int:restaurant_pk>/menus/<pk>/',
         views.MenuDetail.as_view()),
    path('<int:restaurant_pk>/menus/<int:menu_pk>/sections/',
         views.MenuSectionList.as_view()),
    path('<int:restaurant_pk>/menus/<int:menu_pk>/sections/<pk>/',
         views.MenuSectionDetail.as_view()),
    path('<int:restaurant_pk>/menus/<int:menu_pk>/sections/'
         '<int:menusection_pk>/items/',
         views.MenuItemList.as_view()),
    path('<int:restaurant_pk>/menus/<int:menu_pk>/sections/'
         '<int:menuitem_pk>/items/<pk>/',
         views.MenuItemDetail.as_view()),
    ]
