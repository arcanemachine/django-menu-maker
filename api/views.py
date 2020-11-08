from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .permissions import HasRestaurantPermissionsOrReadOnly
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class RestaurantList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Restaurant.objects.all()
    serializer_class = serializers.RestaurantSerializer


class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = Restaurant.objects.all()
    serializer_class = serializers.RestaurantSerializer


class MenuList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    serializer_class = serializers.MenuSerializer


class MenuDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer


class MenuSectionList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = MenuSection.objects.all()
    serializer_class = serializers.MenuSectionSerializer


class MenuSectionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = MenuSection.objects.all()
    serializer_class = serializers.MenuSectionSerializer


class MenuItemList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
