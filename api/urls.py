from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('restaurants', views.RestaurantViewSet, basename='restaurants')
router.register('menus', views.MenuViewSet, basename='menus')

urlpatterns = router.urls
