from django.urls import path

from . import views

app_name = 'menus'

urlpatterns = [
    path('',
        views.RestaurantMenuListView.as_view(),
        name='restaurant_menu_list'),
    path('<slug:menu_slug>/',
        views.MenuDetailView.as_view(),
        name='menu_detail'),
]
