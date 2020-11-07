from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import HasRestaurantPermissionsOrReadOnly
from .serializers import RestaurantSerializer, MenuSerializer
from restaurants.models import Restaurant
from menus.models import Menu


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        permission_classes = [HasRestaurantPermissionsOrReadOnly]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
