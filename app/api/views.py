from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .permissions import HasRestaurantPermissionsOrReadOnly
from menus_project.constants import FRONTEND_SERVER_URL_CONFIRM_EMAIL
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem

UserModel = get_user_model()


def api_root(request):
    return HttpResponseRedirect(reverse('api:restaurant_list'))


def verify_email_view(request, key):
    return HttpResponseRedirect(FRONTEND_SERVER_URL_CONFIRM_EMAIL + key)


def is_username_available(request, username):
    if not UserModel.objects.filter(username=username).exists():
        return JsonResponse({'isUsernameAvailable': True})
    else:
        return JsonResponse({'isUsernameAvailable': False})


def is_email_available(request, email):
    if not UserModel.objects.filter(email=email).exists():
        return JsonResponse({'isEmailAvailable': True})
    else:
        return JsonResponse({'isEmailAvailable': False})


class RestaurantList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Restaurant.objects.all()
    serializer_class = serializers.RestaurantSerializer


class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'restaurant_pk'
    serializer_class = serializers.RestaurantSerializer

    def get_queryset(self):
        return Restaurant.objects.filter(pk=self.kwargs['restaurant_pk'])


class MenuList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'restaurant_pk'
    serializer_class = serializers.MenuSerializer

    def check_permissions(self, request):
        super().check_permissions(request)
        obj = Restaurant.objects.get(pk=self.kwargs['restaurant_pk'])
        super().check_object_permissions(request, obj)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['restaurant_pk'] = self.kwargs['restaurant_pk']
        return context

    def get_queryset(self):
        return Menu.objects.filter(restaurant__pk=self.kwargs['restaurant_pk'])


class MenuDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    serializer_class = serializers.MenuSerializer

    def get_queryset(self):
        return Menu.objects.filter(pk=self.kwargs['menu_pk'])


class MenuSectionList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    serializer_class = serializers.MenuSectionSerializer

    def check_permissions(self, request):
        super().check_permissions(request)
        obj = Restaurant.objects.get(pk=self.kwargs['restaurant_pk'])
        super().check_object_permissions(request, obj)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['menu_pk'] = self.kwargs['menu_pk']
        return context

    def get_queryset(self):
        return MenuSection.objects.filter(menu__pk=self.kwargs['menu_pk'])


class MenuSectionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menusection_pk'
    serializer_class = serializers.MenuSectionSerializer

    def get_queryset(self):
        return MenuSection.objects.filter(pk=self.kwargs['menusection_pk'])


class MenuItemList(generics.ListCreateAPIView):
    permission_classes = [HasRestaurantPermissionsOrReadOnly]
    lookup_url_kwarg = 'menu_pk'
    serializer_class = serializers.MenuItemSerializer

    def check_permissions(self, request):
        super().check_permissions(request)
        obj = Restaurant.objects.get(pk=self.kwargs['restaurant_pk'])
        super().check_object_permissions(request, obj)

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
    serializer_class = serializers.MenuItemSerializer

    def get_queryset(self):
        return MenuItem.objects.filter(pk=self.kwargs['menuitem_pk'])
