from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('r', views.RestaurantViewSet, basename='restaurants')
router.register('m', views.MenuViewSet, basename='menus')
router.register('ms', views.MenuSectionViewSet, basename='menusections')

urlpatterns = router.urls
