from django.urls import reverse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APITestCase

import factories as f
from . import serializers, views
from .permissions import HasRestaurantPermissionsOrReadOnly
from menus_project import constants
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class RestaurantListTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.RestaurantList

        # create model objects
        cls.test_user = f.UserFactory()
        cls.test_restaurants = f.RestaurantFactory.create_batch(3)

        # generate test url
        cls.current_test_url = reverse('api:restaurant_list')

    def setUp(self):
        self.client.login(username=self.test_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'RestaurantList')

    def test_view_parent_class(self):
        self.assertEqual(self.view.__bases__[-1], generics.ListCreateAPIView)

    def test_permission_classes(self):
        self.assertEqual(self.view.permission_classes, [IsAuthenticated])

    def test_queryset(self):
        self.assertEqual(
            repr(self.view.queryset), repr(Restaurant.objects.all()))

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.RestaurantSerializer)

    def test_request_get_method_list_objects(self):
        # get expected objects from serializer
        restaurants = Restaurant.objects.all()
        serializer = serializers.RestaurantSerializer(restaurants, many=True)

        # get actual objects from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the actual result
        self.assertEqual(self.response.data, serializer.data)

    def test_request_post_method_create_object(self):
        post_data = {'name': 'Created Restaurant'}

        # create a new object, with a before-and-after count
        old_restaurant_count = Restaurant.objects.count()
        self.response = self.client.post(self.current_test_url, post_data)
        new_restaurant_count = Restaurant.objects.count()

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(old_restaurant_count + 1, new_restaurant_count)

        # new object has correct parameters
        self.assertEqual(self.response.data['name'], post_data['name'])
        self.assertTrue(
            self.response.data['admin_users'], [self.test_user.pk])


class RestaurantDetailTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.RestaurantDetail

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_restaurant = \
            f.RestaurantFactory(admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {'restaurant_pk': cls.test_restaurant.pk}
        cls.current_test_url = \
            reverse('api:restaurant_detail', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'RestaurantDetail')

    def test_view_parent_class(self):
        self.assertEqual(
            self.view.__bases__[-1], generics.RetrieveUpdateDestroyAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'restaurant_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.RestaurantSerializer)

    # request methods
    def test_request_get_method_retrieve_object(self):
        # get expected result from serializer
        restaurant = Restaurant.objects.filter(pk=self.test_restaurant.pk)
        serializer = serializers.RestaurantSerializer(restaurant, many=True)

        # get result from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the result
        self.assertEqual(self.response.data, dict(serializer.data[0]))

    def test_request_put_method_update_object(self):
        post_data = {'name': 'Updated Restaurant Name'}

        old_restaurant_count = Restaurant.objects.count()
        self.response = self.client.put(self.current_test_url, post_data)
        new_restaurant_count = Restaurant.objects.count()

        # object updated successfully
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(old_restaurant_count, new_restaurant_count)

        # new object has correct parameters
        self.assertEqual(self.response.data['name'], post_data['name'])

    def test_request_delete_method_destroy_object(self):
        # create object to delete
        self.restaurant_to_delete = f.RestaurantFactory()

        # generate new test url
        self.kwargs = {'restaurant_pk': self.test_restaurant.pk}
        self.current_test_url = \
            reverse('api:restaurant_detail', kwargs=self.kwargs)

        # delete the object
        old_restaurant_count = Restaurant.objects.count()
        self.response = self.client.delete(self.current_test_url)
        new_restaurant_count = Restaurant.objects.count()

        # object deleted successfully, and object count decreased by one
        self.assertEqual(self.response.status_code, 204)
        self.assertEqual(old_restaurant_count - 1, new_restaurant_count)


class MenuListTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuList

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_restaurant = f.RestaurantFactory()
        cls.test_menus = f.MenuFactory.create_batch(
            size=3,
            restaurant=cls.test_restaurant,
            admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {'restaurant_pk': cls.test_menus[0].pk}
        cls.current_test_url = reverse('api:menu_list', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuList')

    def test_view_parent_class(self):
        self.assertEqual(self.view.__bases__[-1], generics.ListCreateAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'restaurant_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuSerializer)

    # request methods
    def test_get_method_list_objects(self):
        # get expected objects from serializer
        menus = Menu.objects.filter(restaurant__pk=self.test_restaurant.pk)
        serializer = serializers.MenuSerializer(menus, many=True)

        # get actual objects from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the actual result
        self.assertEqual(self.response.data, serializer.data)

    def test_request_post_method_create_object(self):
        post_data = {'name': 'Created Menu'}

        # create a new object, with a before-and-after count
        old_menu_count = Menu.objects.count()
        self.response = self.client.post(self.current_test_url, post_data)
        new_menu_count = Menu.objects.count()

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(old_menu_count + 1, new_menu_count)

        # new object has correct parameters
        self.assertEqual(
            self.response.data['restaurant_name'], self.test_restaurant.name)
        self.assertEqual(self.response.data['name'], post_data['name'])


class MenuDetailTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuDetail

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menu = f.MenuFactory(admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {'restaurant_pk': cls.test_menu.restaurant.pk,
                      'menu_pk': cls.test_menu.pk}
        cls.current_test_url = \
            reverse('api:menu_detail', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuDetail')

    def test_view_parent_class(self):
        self.assertEqual(
            self.view.__bases__[-1], generics.RetrieveUpdateDestroyAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'menu_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuSerializer)

    def test_get_method_response_data(self):
        menu = Menu.objects.get(pk=self.test_menu.pk)
        serializer = serializers.MenuSerializer(menu)
        self.assertEqual(self.response.data, serializer.data)
        self.assertEqual(self.response.status_code, 200)

    # request methods
    def test_request_get_method_retrieve_object(self):
        # get expected result from serializer
        menu = Menu.objects.filter(pk=self.test_menu.pk)
        serializer = serializers.MenuSerializer(menu, many=True)

        # get result from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the result
        self.assertEqual(self.response.data, dict(serializer.data[0]))

    def test_request_put_method_update_object(self):
        post_data = {'name': 'Updated Menu Name'}

        old_menu_count = Menu.objects.count()
        self.response = self.client.put(self.current_test_url, post_data)
        new_menu_count = Menu.objects.count()

        # object updated successfully
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(old_menu_count, new_menu_count)

        # new object has correct parameters
        self.assertEqual(self.response.data['name'], post_data['name'])

    def test_request_delete_method_destroy_object(self):
        # create object to delete
        self.menu_to_delete = f.MenuFactory()

        # generate new test url
        self.kwargs = {'restaurant_pk': self.test_menu.restaurant.pk,
                       'menu_pk': self.test_menu.pk}
        self.current_test_url = \
            reverse('api:menu_detail', kwargs=self.kwargs)

        # delete the object
        old_menu_count = Menu.objects.count()
        self.response = self.client.delete(self.current_test_url)
        new_menu_count = Menu.objects.count()

        # object deleted successfully, and object count decreased by one
        self.assertEqual(self.response.status_code, 204)
        self.assertEqual(old_menu_count - 1, new_menu_count)


class MenuSectionListTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuSectionList

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menu = f.MenuFactory()
        cls.test_menusections = f.MenuSectionFactory.create_batch(
            size=3,
            menu=cls.test_menu,
            admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {'restaurant_pk': cls.test_menu.restaurant.pk,
                      'menu_pk': cls.test_menu.pk}
        cls.current_test_url = \
            reverse('api:menusection_list', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuSectionList')

    def test_view_parent_class(self):
        self.assertEqual(self.view.__bases__[-1], generics.ListCreateAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'menu_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuSectionSerializer)

    # request methods
    def test_get_method_list_objects(self):
        # get expected objects from serializer
        menusections = \
            MenuSection.objects.filter(menu__pk=self.test_menu.pk)
        serializer = serializers.MenuSectionSerializer(menusections, many=True)

        # get actual objects from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the actual result
        self.assertEqual(self.response.data, serializer.data)

    def test_request_post_method_create_object(self):
        post_data = {'name': 'Created Menu Section'}

        # create a new object, with a before-and-after count
        old_menusection_count = MenuSection.objects.count()
        self.response = self.client.post(self.current_test_url, post_data)
        new_menusection_count = MenuSection.objects.count()

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(old_menusection_count + 1, new_menusection_count)

        # new object has correct parameters
        self.assertEqual(
            self.response.data['menu_name'], self.test_menu.name)
        self.assertEqual(self.response.data['name'], post_data['name'])


class MenuSectionDetailTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuSectionDetail

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menusection = \
            f.MenuSectionFactory(admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {'restaurant_pk': cls.test_menusection.menu.restaurant.pk,
                      'menu_pk': cls.test_menusection.menu.pk,
                      'menusection_pk': cls.test_menusection.pk}
        cls.current_test_url = \
            reverse('api:menusection_detail', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuSectionDetail')

    def test_view_parent_class(self):
        self.assertEqual(
            self.view.__bases__[-1], generics.RetrieveUpdateDestroyAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'menusection_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuSectionSerializer)

    # request methods
    def test_request_get_method_retrieve_object(self):
        # get expected result from serializer
        menusection = MenuSection.objects.filter(pk=self.test_menusection.pk)
        serializer = serializers.MenuSectionSerializer(menusection, many=True)

        # get result from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the result
        self.assertEqual(self.response.data, dict(serializer.data[0]))

    def test_request_put_method_update_object(self):
        post_data = {'name': 'Updated Menu Section Name'}

        old_menusection_count = MenuSection.objects.count()
        self.response = self.client.put(self.current_test_url, post_data)
        new_menusection_count = MenuSection.objects.count()

        # object updated successfully
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(old_menusection_count, new_menusection_count)

        # new object has correct parameters
        self.assertEqual(self.response.data['name'], post_data['name'])

    def test_request_delete_method_destroy_object(self):
        # create object to delete
        self.menusection_to_delete = f.MenuSectionFactory()

        # generate new test url
        self.kwargs = {
            'restaurant_pk': self.test_menusection.menu.restaurant.pk,
            'menu_pk': self.test_menusection.menu.pk,
            'menusection_pk': self.test_menusection.pk}
        self.current_test_url = \
            reverse('api:menusection_detail', kwargs=self.kwargs)

        # delete the object
        old_menusection_count = MenuSection.objects.count()
        self.response = self.client.delete(self.current_test_url)
        new_menusection_count = MenuSection.objects.count()

        # object deleted successfully, and object count decreased by one
        self.assertEqual(self.response.status_code, 204)
        self.assertEqual(old_menusection_count - 1, new_menusection_count)


class MenuItemListTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuItemList

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menusection = f.MenuSectionFactory()
        cls.test_menuitems = f.MenuItemFactory.create_batch(
            size=3,
            menusection=cls.test_menusection,
            admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {
            'restaurant_pk':
                cls.test_menuitems[0].menusection.menu.restaurant.pk,
            'menu_pk': cls.test_menuitems[0].menusection.menu.pk,
            'menusection_pk': cls.test_menuitems[0].menusection.pk}
        cls.current_test_url = \
            reverse('api:menuitem_list', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuItemList')

    def test_view_parent_class(self):
        self.assertEqual(self.view.__bases__[-1], generics.ListCreateAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'menu_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuItemSerializer)

    # request methods
    def test_get_method_list_objects(self):
        # get expected objects from serializer
        menuitems = MenuItem.objects.filter(
            menusection__pk=self.test_menusection.pk)
        serializer = serializers.MenuItemSerializer(menuitems, many=True)

        # get actual objects from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the actual result
        self.assertEqual(self.response.data, serializer.data)

    def test_request_post_method_create_object(self):
        post_data = {'name': 'Created Menu Item'}

        # create a new object, with a before-and-after count
        old_menuitem_count = MenuItem.objects.count()
        self.response = self.client.post(self.current_test_url, post_data)
        new_menuitem_count = MenuItem.objects.count()

        # new object created successfully
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(old_menuitem_count + 1, new_menuitem_count)

        # new object has correct parameters
        self.assertEqual(
            self.response.data['menusection_name'], self.test_menusection.name)
        self.assertEqual(self.response.data['name'], post_data['name'])


class MenuItemDetailTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.view = views.MenuItemDetail

        # create model objects
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_menuitem = \
            f.MenuItemFactory(admin_users=[cls.restaurant_admin_user])

        # generate test url
        cls.kwargs = {
            'restaurant_pk': cls.test_menuitem.menusection.menu.restaurant.pk,
            'menu_pk': cls.test_menuitem.menusection.menu.pk,
            'menusection_pk': cls.test_menuitem.menusection.pk,
            'menuitem_pk': cls.test_menuitem.pk}
        cls.current_test_url = \
            reverse('api:menuitem_detail', kwargs=cls.kwargs)

    def setUp(self):
        self.client.login(username=self.restaurant_admin_user.username,
                          password=constants.TEST_USER_PASSWORD)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'MenuItemDetail')

    def test_view_parent_class(self):
        self.assertEqual(
            self.view.__bases__[-1], generics.RetrieveUpdateDestroyAPIView)

    def test_permission_classes(self):
        self.assertEqual(
            self.view.permission_classes, [HasRestaurantPermissionsOrReadOnly])

    def test_lookup_url_kwarg(self):
        self.assertEqual(self.view.lookup_url_kwarg, 'menuitem_pk')

    def test_serializer_class(self):
        self.assertEqual(
            self.view.serializer_class, serializers.MenuItemSerializer)

    # request methods
    def test_request_get_method_retrieve_object(self):
        # get expected result from serializer
        menuitem = MenuItem.objects.filter(pk=self.test_menuitem.pk)
        serializer = serializers.MenuItemSerializer(menuitem, many=True)

        # get result from view
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 200)

        # compare the expected result with the result
        self.assertEqual(self.response.data, dict(serializer.data[0]))

    def test_request_put_method_update_object(self):
        post_data = {'name': 'Updated Menu Item Name',
                     'description': 'Updated Menu Item Description'}

        old_menuitem_count = MenuItem.objects.count()
        self.response = self.client.put(self.current_test_url, post_data)
        new_menuitem_count = MenuItem.objects.count()

        # object updated successfully
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(old_menuitem_count, new_menuitem_count)

        # new object has correct parameters
        self.assertEqual(self.response.data['name'], post_data['name'])

    def test_request_delete_method_destroy_object(self):
        # create object to delete
        self.menuitem_to_delete = f.MenuItemFactory()

        # generate new test url
        self.kwargs = {
            'restaurant_pk': self.test_menuitem.menusection.menu.restaurant.pk,
            'menu_pk': self.test_menuitem.menusection.menu.pk,
            'menusection_pk': self.test_menuitem.menusection.pk,
            'menuitem_pk': self.test_menuitem.pk}
        self.current_test_url = \
            reverse('api:menuitem_detail', kwargs=self.kwargs)

        # delete the object
        old_menuitem_count = MenuItem.objects.count()
        self.response = self.client.delete(self.current_test_url)
        new_menuitem_count = MenuItem.objects.count()

        # object deleted successfully, and object count decreased by one
        self.assertEqual(self.response.status_code, 204)
        self.assertEqual(old_menuitem_count - 1, new_menuitem_count)
