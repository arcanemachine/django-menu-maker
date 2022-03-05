from django.urls import path

from . import views

app_name = 'menus'

urlpatterns = [
    path('',
         views.menus_root,
         name='menus_root'),
    path('new-menu/',
         views.MenuCreateView.as_view(),
         name='menu_create'),
    path('<slug:menu_slug>/',
         views.MenuDetailView.as_view(),
         name='menu_detail'),
    path('<slug:menu_slug>/edit/',
         views.MenuUpdateView.as_view(),
         name='menu_update'),
    path('<slug:menu_slug>/delete/',
         views.MenuDeleteView.as_view(),
         name='menu_delete'),
    path('<slug:menu_slug>/new-section/',
         views.MenuSectionCreateView.as_view(),
         name='menusection_create'),
    path('<slug:menu_slug>/<slug:menusection_slug>/',
         views.MenuSectionDetailView.as_view(),
         name='menusection_detail'),
    path('<slug:menu_slug>/<slug:menusection_slug>/edit/',
         views.MenuSectionUpdateView.as_view(),
         name='menusection_update'),
    path('<slug:menu_slug>/<slug:menusection_slug>/delete/',
         views.MenuSectionDeleteView.as_view(),
         name='menusection_delete'),
    path('<slug:menu_slug>/<slug:menusection_slug>/new-item/',
         views.MenuItemCreateView.as_view(),
         name='menuitem_create'),
    path('<slug:menu_slug>/<slug:menusection_slug>/<slug:menuitem_slug>/',
         views.MenuItemDetailView.as_view(),
         name='menuitem_detail'),
    path('<slug:menu_slug>/<slug:menusection_slug>/<slug:menuitem_slug>/edit/',
         views.MenuItemUpdateView.as_view(),
         name='menuitem_update'),
    path('<slug:menu_slug>/<slug:menusection_slug>/'
         '<slug:menuitem_slug>/delete/',
         views.MenuItemDeleteView.as_view(),
         name='menuitem_delete'),
]
