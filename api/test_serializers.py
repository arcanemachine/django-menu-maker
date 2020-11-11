from django.urls import reverse
from rest_framework.test import APITestCase

import factories as f
from menus_project import constants as c
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem
from . import serializers


class RestaurantSerializerTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.RestaurantSerializer
        cls.restaurant_admin_user = f.UserFactory()

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'Restaurant')

    def test_meta_fields(self):
        self.assertEqual(self.serializer.Meta.fields,
                         ['id', 'name', 'admin_users', 'menu_set'])

    def test_meta_read_only_fields(self):
        self.assertEqual(self.serializer.Meta.read_only_fields,
                         ['admin_users', 'menu_set'])

    def test_method_create(self):
        self.current_test_url = reverse('api:restaurant_list')

        # get object count before creating new object
        old_restaurant_count = Restaurant.objects.count()

        # create new restaurant
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=c.TEST_USER_PASSWORD)
        self.response = self.client.post(
            self.current_test_url, {'name': c.TEST_RESTAURANT_NAME})

        # new restaurant created successfully
        self.assertEqual(self.response.status_code, 201)

        # object has proper admin_users
        self.test_restaurant = \
            Restaurant.objects.get(name=c.TEST_RESTAURANT_NAME)
        self.assertEqual(self.test_restaurant.admin_users.count(), 1)
        self.assertIn(
            self.restaurant_admin_user, self.test_restaurant.admin_users.all())

        # object count increased by 1
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count + 1, new_restaurant_count)


class MenuSerializerTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuSerializer

        cls.restaurant_admin_user = f.UserFactory()
        cls.test_restaurant = \
            f.RestaurantFactory(admin_users=[cls.restaurant_admin_user])

    def test_fields_contain_restaurant_name(self):
        self.assertTrue('restaurant_name' in self.serializer.Meta.fields)

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'Menu')

    def test_meta_fields(self):
        self.assertEqual(
            self.serializer.Meta.fields,
            ['id', 'name', 'menusection_set', 'restaurant_name'])

    def test_meta_read_only_fields(self):
        self.assertTrue(
            self.serializer.Meta.read_only_fields,
            ['menusection_set', 'restaurant_name'])

    def test_method_create_adds_new_menu_to_restaurant(self):
        self.current_test_url = reverse('api:menu_list', kwargs={
            'restaurant_pk': self.test_restaurant.pk})
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=c.TEST_USER_PASSWORD)

        # get object count before creating new object
        old_menu_count = Menu.objects.count()

        # create new object
        self.response = self.client.post(
            self.current_test_url, {'name': c.TEST_MENU_NAME})

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)

        # object has proper parent
        self.test_menu = Menu.objects.get(name=c.TEST_MENU_NAME)
        self.assertEqual(self.test_menu.restaurant, self.test_restaurant)

        # object count increased by 1
        new_menu_count = Menu.objects.count()
        self.assertEqual(old_menu_count + 1, new_menu_count)


class MenuSectionSerializerTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuSectionSerializer

        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menu = f.MenuFactory(admin_users=[cls.restaurant_admin_user])

    def test_fields_contain_restaurant_name(self):
        self.assertTrue('restaurant_name' in self.serializer.Meta.fields)

    def test_fields_contain_menu_name(self):
        self.assertTrue('menu_name' in self.serializer.Meta.fields)

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'MenuSection')

    def test_meta_fields(self):
        self.assertEqual(
            self.serializer.Meta.fields,
            ['id', 'name', 'menuitem_set', 'restaurant_name', 'menu_name'])

    def test_meta_read_only_fields(self):
        self.assertTrue(
            self.serializer.Meta.read_only_fields,
            ['menuitem_set', 'restaurant_name', 'menu_name'])

    def test_method_create_adds_menu_to_menusection(self):
        self.current_test_url = reverse('api:menusection_list', kwargs={
            'restaurant_pk': self.test_menu.restaurant.pk,
            'menu_pk': self.test_menu.pk})

        # get object count before creating new object
        old_menusection_count = MenuSection.objects.count()

        # create new object
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=c.TEST_USER_PASSWORD)
        self.response = self.client.post(
            self.current_test_url, {'name': c.TEST_MENUSECTION_NAME})

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)

        # object has proper parent
        self.test_menusection = \
            MenuSection.objects.get(name=c.TEST_MENUSECTION_NAME)
        self.assertEqual(self.test_menusection.menu, self.test_menu)

        # object count increased by 1
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count + 1, new_menusection_count)


class MenuItemSerializerTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuItemSerializer

        # create objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menusection = \
            f.MenuSectionFactory(admin_users=[cls.restaurant_admin_user])

    def test_fields_contain_restaurant_name(self):
        self.assertTrue('restaurant_name' in self.serializer.Meta.fields)

    def test_fields_contain_menu_name(self):
        self.assertTrue('menu_name' in self.serializer.Meta.fields)

    def test_fields_contain_menusection_name(self):
        self.assertTrue('menusection_name' in self.serializer.Meta.fields)

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'MenuItem')

    def test_meta_fields(self):
        self.assertEqual(
            self.serializer.Meta.fields,
            ['id', 'name', 'description', 'restaurant_name', 'menu_name',
                'menusection_name'])

    def test_meta_read_only_fields(self):
        self.assertTrue(
            self.serializer.Meta.read_only_fields,
            ['menuitem_set', 'restaurant_name', 'menu_name'])

    def test_method_create_adds_menusection_to_menuitem(self):
        self.current_test_url = reverse('api:menuitem_list', kwargs={
            'restaurant_pk': self.test_menusection.menu.restaurant.pk,
            'menu_pk': self.test_menusection.menu.pk,
            'menusection_pk': self.test_menusection.pk})
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=c.TEST_USER_PASSWORD)

        # get object count before creating new object
        old_menuitem_count = MenuItem.objects.count()

        # create new object
        self.response = self.client.post(
            self.current_test_url, {
                'name': c.TEST_MENUITEM_NAME,
                'description': c.TEST_MENUITEM_DESCRIPTION})

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)

        # object has proper parent
        self.test_menuitem = \
            MenuItem.objects.get(name=c.TEST_MENUITEM_NAME)
        self.assertEqual(self.test_menuitem.menusection, self.test_menusection)

        # object count increased by 1
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count + 1, new_menuitem_count)
