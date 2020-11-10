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
    lookup_url_kwarg = 'restaurant_pk'
    queryset = Restaurant.objects.all()
    serializer_class = serializers.RestaurantSerializer


class MenuList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'restaurant_pk'
    serializer_class = serializers.MenuSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['restaurant_pk'] = self.kwargs['restaurant_pk']
        return context

    def get_queryset(self):
        return Menu.objects.filter(restaurant__pk=self.kwargs['restaurant_pk'])


class MenuDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer


class MenuSectionList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    serializer_class = serializers.MenuSectionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['menu_pk'] = self.kwargs['menu_pk']
        return context

    def get_queryset(self):
        return MenuSection.objects.filter(menu__pk=self.kwargs['menu_pk'])


class MenuSectionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menusection_pk'
    queryset = MenuSection.objects.all()
    serializer_class = serializers.MenuSectionSerializer


class MenuItemList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    serializer_class = serializers.MenuItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['menusection_pk'] = self.kwargs['menusection_pk']
        return context

    def get_queryset(self):
        return MenuItem.objects.filter(
            menusection=self.kwargs['menusection_pk'])


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menuitem_pk'
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
