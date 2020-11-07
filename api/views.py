from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .permissions import HasRestaurantPermissionsOrReadOnly
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = serializers.RestaurantSerializer

    def get_permissions(self):
        permission_classes = [HasRestaurantPermissionsOrReadOnly]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer
    permission_classes = [HasRestaurantPermissionsOrReadOnly]


class MenuSectionViewSet(viewsets.ModelViewSet):
    queryset = MenuSection.objects.all()
    serializer_class = serializers.MenuSectionSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
