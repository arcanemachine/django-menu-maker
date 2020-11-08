from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('',
         views.RestaurantList.as_view()),
    path('<pk>/',
         views.RestaurantDetail.as_view()),
    path('<int:restaurant_pk>/m/',
         views.MenuList.as_view()),
    path('<int:restaurant_pk>/m/<pk>/',
         views.MenuDetail.as_view()),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/',
         views.MenuSectionList.as_view()),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<pk>/',
         views.MenuSectionDetail.as_view()),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/',
         views.MenuItemList.as_view()),
    path('<int:restaurant_pk>/m/<int:menu_pk>/s/<int:menusection_pk>/i/<pk>/',
         views.MenuItemDetail.as_view()),
    ]
