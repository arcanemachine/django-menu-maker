from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('', views.RestaurantViewSet, basename='restaurants')

urlpatterns = router.urls
