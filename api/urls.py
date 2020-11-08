from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('r', views.RestaurantViewSet, basename='restaurants')
router.register('m', views.MenuViewSet, basename='menus')
router.register('ms', views.MenuSectionViewSet, basename='menusections')
router.register('mi', views.MenuItemViewSet, basename='menuitems')

urlpatterns = [
    path('m/', views.MenuViewSet.as_view({'get': 'list'})),
    path('ms/', views.MenuSectionViewSet.as_view({'get': 'list'})),
    path('mi/', views.MenuItemViewSet.as_view({'get': 'list'})),
    ]

urlpatterns += router.urls
