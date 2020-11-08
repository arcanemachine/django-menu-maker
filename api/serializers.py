from rest_framework import serializers

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'admin_users', 'menu_set']
        read_only_fields = ['admin_users', 'menu_set']

    def create(self, validated_data):
        """
        Create a new restaurant and add the creator to admin_users.
        """
        self.user = self.context['request'].user
        restaurant = Restaurant.objects.create(**validated_data)
        restaurant.admin_users.add(self.user)
        return restaurant


class MenuSerializer(serializers.ModelSerializer):

    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Menu
        fields = ['id', 'name', 'restaurant', 'restaurant_name',
            'menusection_set']
        read_only_fields = ['restaurant', 'menusection_set']


class MenuSectionSerializer(serializers.ModelSerializer):

    restaurant_name = \
        serializers.ReadOnlyField(source='menu.restaurant.name')
    menu_name = serializers.ReadOnlyField(source='menu.name')

    class Meta:
        model = MenuSection
        fields = ['id', 'restaurant_name', 'menu_name', 'name', 'menuitem_set']
        read_only_fields = ['menuitem_set']


class MenuItemSerializer(serializers.ModelSerializer):

    restaurant_name = \
        serializers.ReadOnlyField(source='menusection.menu.restaurant.name')
    menu_name = serializers.ReadOnlyField(source='menusection.menu.name')
    menusection_name = serializers.ReadOnlyField(source='menusection.name')

    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant_name', 'menu_name', 'menusection_name',
            'name', 'description']
