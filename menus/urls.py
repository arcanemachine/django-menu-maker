from django.urls import path

from . import views

app_name = 'menus'

urlpatterns = [
    path('',
        views.menus_root,
        name='menus_root'),
    path('<slug:menu_slug>/',
        views.MenuDetailView.as_view(),
        name='menu_detail'),
    path('<slug:menu_slug>/new-section/',
        views.MenuSectionCreateView.as_view(),
        name='menusection_create'),
    path('<slug:menu_slug>/<slug:menusection_slug>/',
        views.MenuSectionDetailView.as_view(),
        name='menusection_detail'),
]
