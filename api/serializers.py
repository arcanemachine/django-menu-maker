from rest_framework import serializers

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem

class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'admin_users', 'menu_set']
        read_only_fields = ['admin_users', 'menu_set']

class MenuSerializer(serializers.ModelSerializer):

    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Menu
        fields = ['id', 'name', 'restaurant_name', 'menusection_set']
        read_only_fields = ['name', 'menusection_set']
