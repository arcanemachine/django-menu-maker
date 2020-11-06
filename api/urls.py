from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('', views.RestaurantList.as_view()),
    ]
