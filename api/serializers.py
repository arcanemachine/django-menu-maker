from rest_framework import serializers

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'admin_users', 'menu_set']
        read_only_fields = ['admin_users', 'menu_set']

    def create(self, validated_data):
        self.user = self.context['request'].user
        restaurant = Restaurant.objects.create(**validated_data)
        restaurant.admin_users.add(self.user)
        return restaurant


class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Menu
        fields = \
            ['id', 'name', 'menusection_set', 'restaurant_name']
        read_only_fields = ['menusection_set', 'restaurant_name']

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs \
                and kwargs['context'].get('restaurant_pk'):
            self.restaurant = \
                Restaurant.objects.get(pk=kwargs['context']['restaurant_pk'])
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        menu = Menu.objects.create(
            restaurant=self.restaurant, **validated_data)
        return menu


class MenuSectionSerializer(serializers.ModelSerializer):
    restaurant_name = \
        serializers.ReadOnlyField(source='menu.restaurant.name')
    menu_name = serializers.ReadOnlyField(source='menu.name')

    class Meta:
        model = MenuSection
        fields = ['id', 'name', 'menuitem_set', 'restaurant_name', 'menu_name']
        read_only_fields = ['menuitem_set', 'restaurant_name', 'menu_name']

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs and kwargs['context'].get('menu_pk'):
            self.menu = Menu.objects.get(pk=kwargs['context']['menu_pk'])
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        menusection = MenuSection.objects.create(
            menu=self.menu, **validated_data)
        return menusection


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = \
        serializers.ReadOnlyField(source='menusection.menu.restaurant.name')
    menu_name = serializers.ReadOnlyField(source='menusection.menu.name')
    menusection_name = serializers.ReadOnlyField(source='menusection.name')

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'restaurant_name',
                  'menu_name', 'menusection_name']
        read_only_fields = ['restaurant_name', 'menu_name', 'menusection_name']

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs \
                and kwargs['context'].get('menusection_pk'):
            self.menusection = \
                MenuSection.objects.get(pk=kwargs['context']['menusection_pk'])
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        menuitem = MenuItem.objects.create(
            menusection=self.menusection, **validated_data)
        return menuitem
