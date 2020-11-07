from rest_framework import serializers

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem

class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'admin_users', 'menu_set']
        read_only_fields = ['admin_users', 'menu_set']

class MenuSerializer(serializers.ModelSerializer):

    restaurant_slug = serializers.ReadOnlyField(source='restaurant.slug')
    menusections = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='slug')

    class Meta:
        model = Menu
        fields = ['id', 'slug', 'restaurant_slug', 'name', 'menusections']
        read_only_fields = ['name', 'restaurant_slug', 'menusections']
