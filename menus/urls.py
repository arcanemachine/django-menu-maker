from django.urls import path

from . import views

app_name = 'menus'

urlpatterns = [
    path('<slug:menu_slug>/',
        views.MenuDetailView.as_view(),
        name='menu_detail'),
]
