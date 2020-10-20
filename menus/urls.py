from django.urls import path

from . import views

app_name = 'menus'

urlpatterns = [
    
    path('hello/', views.hello, name="hello"),

    ]
