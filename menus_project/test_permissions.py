from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse

import factories as f
from .permissions import UserHasRestaurantPermissionsMixin


class UserHasRestaurantPermissionsMixinTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_permission = UserHasRestaurantPermissionsMixin()
        cls.request = RequestFactory().get('/')

        # create users
        cls.test_user = f.UserFactory()
        cls.restaurant_admin_user = f.UserFactory()
        cls.admin_user = f.UserFactory(is_staff=True)

        # create restaurant objects
        cls.test_restaurant = \
            f.RestaurantFactory(admin_users=[cls.restaurant_admin_user])
        cls.test_menu = f.MenuFactory(restaurant=cls.test_restaurant)
        cls.test_menusection = f.MenuSectionFactory(menu=cls.test_menu)
        cls.test_menuitem = f.MenuItemFactory(menusection=cls.test_menusection)


    # restaurant object
    def test_unauthenticated_user_restaurant_object_returns_false(self):
        self.request.user = AnonymousUser()
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_restaurant))

    def test_authenticated_user_restaurant_object_returns_false(self):
        self.request.user = self.test_user
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_restaurant))

    def test_authorized_user_restaurant_object_returns_true(self):
        self.request.user = self.restaurant_admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_restaurant))

    def test_admin_user_restaurant_object_returns_true(self):
        self.request.user = self.admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_restaurant))

    # menu object
    def test_unauthenticated_user_menu_object_returns_false(self):
        self.request.user = AnonymousUser()
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menu))

    def test_authenticated_user_menu_object_returns_false(self):
        self.request.user = self.test_user
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menu))

    def test_authorized_user_menu_object_returns_true(self):
        self.request.user = self.restaurant_admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menu))

    def test_admin_user_menu_object_returns_true(self):
        self.request.user = self.admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menu))

    # menusection object
    def test_unauthenticated_user_menusection_object_returns_false(self):
        self.request.user = AnonymousUser()
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menusection))

    def test_authenticated_user_menusection_object_returns_false(self):
        self.request.user = self.test_user
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menusection))

    def test_authorized_user_menusection_object_returns_true(self):
        self.request.user = self.restaurant_admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menusection))

    def test_admin_user_menusection_object_returns_true(self):
        self.request.user = self.admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menusection))

    # menuitem object
    def test_unauthenticated_user_menuitem_object_returns_false(self):
        self.request.user = AnonymousUser()
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menuitem))

    def test_authenticated_user_menuitem_object_returns_false(self):
        self.request.user = self.test_user
        self.test_permission.request = self.request
        self.assertFalse(self.test_permission.test_func(self.test_menuitem))

    def test_authorized_user_menuitem_object_returns_true(self):
        self.request.user = self.restaurant_admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menuitem))

    def test_admin_user_menuitem_object_returns_true(self):
        self.request.user = self.admin_user
        self.test_permission.request = self.request
        self.assertTrue(self.test_permission.test_func(self.test_menuitem))

    # bad object
    def test_unauthenticated_user_bad_object_raises_exception(self):
        self.request.user = AnonymousUser()
        self.test_permission.request = self.request
        with self.assertRaises(AttributeError):
            self.test_permission.test_func(self.test_user)

    def test_authenticated_user_bad_object_raises_exception(self):
        self.request.user = self.test_user
        self.test_permission.request = self.request
        with self.assertRaises(AttributeError):
            self.test_permission.test_func(self.test_user)

    def test_authorized_user_bad_object_raises_exception(self):
        self.request.user = self.restaurant_admin_user
        self.test_permission.request = self.request
        with self.assertRaises(AttributeError):
            self.test_permission.test_func(self.test_user)

    def test_admin_user_bad_object_raises_exception(self):
        self.request.user = self.admin_user
        self.test_permission.request = self.request
        with self.assertRaises(AttributeError):
            self.test_permission.test_func(self.test_user)
