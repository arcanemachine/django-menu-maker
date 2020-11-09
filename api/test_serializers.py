from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient  # , APIRequestFactory

import factories
from menus_project import constants
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem
from . import serializers

TEST_USER_PASSWORD = constants.TEST_USER_PASSWORD
TEST_RESTAURANT_NAME = constants.TEST_RESTAURANT_NAME
TEST_MENU_NAME = constants.TEST_MENU_NAME
TEST_MENUSECTION_NAME = constants.TEST_MENUSECTION_NAME
TEST_MENUITEM_NAME = constants.TEST_MENUITEM_NAME
TEST_MENUITEM_DESCRIPTION = constants.TEST_MENUITEM_DESCRIPTION


class RestaurantSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.RestaurantSerializer
        cls.rest_client = APIClient()

        # create objects
        cls.test_user = factories.UserFactory()

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'Restaurant')

    def test_meta_fields(self):
        self.assertEqual(self.serializer.Meta.fields,
                         ['id', 'name', 'admin_users', 'menu_set'])

    def test_meta_read_only_fields(self):
        self.assertEqual(self.serializer.Meta.read_only_fields,
                         ['admin_users', 'menu_set'])

    def test_method_create_adds_registrant_to_admin_users(self):
        self.current_test_url = reverse('api:restaurant_list')

        # create new restaurant
        self.rest_client.login(
            username=self.test_user.username, password=TEST_USER_PASSWORD)
        self.response = self.rest_client.post(self.current_test_url, {
            'name': TEST_RESTAURANT_NAME})

        # new restaurant created successfully
        self.assertEqual(self.response.status_code, 201)

        # get restaurant from pk
        self.test_restaurant = \
            Restaurant.objects.get(name=TEST_RESTAURANT_NAME)

        # restaurant.admin_users contains only the registrant
        self.assertEqual(self.test_restaurant.admin_users.count(), 1)
        self.assertIn(self.test_user, self.test_restaurant.admin_users.all())


class MenuSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuSerializer
        cls.rest_client = APIClient()

        # create objects
        cls.test_user = factories.UserFactory()
        cls.test_restaurant = factories.RestaurantFactory()

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

    def test_method_create_adds_restaurant_to_menu(self):
        self.current_test_url = reverse('api:menu_list', kwargs={
            'restaurant_pk': self.test_restaurant.pk})

        old_menu_count = Menu.objects.count()

        # create new menu
        self.rest_client.login(
            username=self.test_user.username, password=TEST_USER_PASSWORD)
        self.response = self.rest_client.post(
            self.current_test_url, {'name': TEST_MENU_NAME})

        # new menu created successfully
        self.assertEqual(self.response.status_code, 201)

        # menu has proper restaurant
        self.test_menu = Menu.objects.get(name=TEST_MENU_NAME)
        self.assertEqual(self.test_menu.restaurant, self.test_restaurant)

        # menu count increased by 1
        new_menu_count = Menu.objects.count()
        self.assertEqual(old_menu_count + 1, new_menu_count)


class MenuSectionSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuSectionSerializer
        cls.rest_client = APIClient()

        # create objects
        cls.test_user = factories.UserFactory()
        cls.test_menu = factories.MenuFactory()

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

        old_menusection_count = MenuSection.objects.count()

        # create new menusection
        self.rest_client.login(
            username=self.test_user.username, password=TEST_USER_PASSWORD)
        self.response = self.rest_client.post(
            self.current_test_url, {'name': TEST_MENUSECTION_NAME})

        # new menusection created successfully
        self.assertEqual(self.response.status_code, 201)

        # menusection has proper restaurant
        self.test_menusection = \
            MenuSection.objects.get(name=TEST_MENUSECTION_NAME)
        self.assertEqual(self.test_menusection.menu, self.test_menu)

        # menusection count increased by 1
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count + 1, new_menusection_count)


class MenuItemSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = serializers.MenuItemSerializer
        cls.rest_client = APIClient()

        # create objects
        cls.test_user = factories.UserFactory()
        cls.test_menusection = factories.MenuSectionFactory()

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

        old_menuitem_count = MenuItem.objects.count()

        # create new menuitem
        self.rest_client.login(
            username=self.test_user.username, password=TEST_USER_PASSWORD)
        self.response = self.rest_client.post(
            self.current_test_url, {
                'name': TEST_MENUITEM_NAME,
                'description': TEST_MENUITEM_DESCRIPTION})

        # new menuitem created successfully
        self.assertEqual(self.response.status_code, 201)

        # menuitem has proper menusection
        self.test_menuitem = \
            MenuItem.objects.get(name=TEST_MENUITEM_NAME)
        self.assertEqual(self.test_menuitem.menusection, self.test_menusection)

        # menuitem count increased by 1
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count + 1, new_menuitem_count)
