from django.urls import path

from . import views

app_name = 'restaurants'

urlpatterns = [

    path('',
        views.RestaurantListView.as_view(),
        name='restaurant_list'),
    path('<slug:restaurant_slug>/',
        views.RestaurantDetailView.as_view(),
        name='restaurant_detail'),

    #path('<slug:restaurant_slug>/menu/', include('menus.urls'))

    ]
