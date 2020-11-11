from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import permissions

from menus_project import factories as f
from api.permissions import HasRestaurantPermissionsOrReadOnly


class HasRestaurantPermissionsOrReadOnlyTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_permission = HasRestaurantPermissionsOrReadOnly()
        cls.factory = APIRequestFactory()

        # create users
        cls.unprivileged_user = f.UserFactory(username='unprivileged_user')
        cls.permitted_user = f.UserFactory(username='permitted_user')
        cls.admin_user = f.UserFactory(username='admin_user', is_staff=True)

        # create restaurant objects and add permitted user to admin_users
        cls.test_restaurant = f.RestaurantFactory(
            admin_users=[cls.permitted_user])
        cls.test_menu = f.MenuFactory(restaurant=cls.test_restaurant)
        cls.test_menusection = f.MenuSectionFactory(menu=cls.test_menu)
        cls.test_menuitem = f.MenuItemFactory(menusection=cls.test_menusection)

    def test_unauthenticated_user_least_privileged_request_returns_false(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        obj = None

        self.assertFalse(
            self.test_permission.has_object_permission(request, None, obj))

    # sanity check
    def test_authenticated_user_least_privileged_request_returns_true(self):
        request = self.factory.get('/')
        request.user = self.unprivileged_user

        obj = None

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_admin_user_returns_true(self):
        request = self.factory.delete('/')
        request.user = self.admin_user

        obj = None

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_unprivileged_user_can_use_safe_methods(self):
        request = self.factory.get('/')
        request.user = self.unprivileged_user

        obj = None

        self.assertTrue(request.method in permissions.SAFE_METHODS)
        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_permitted_user_with_restaurant_object(self):
        request = self.factory.delete('/')
        request.user = self.permitted_user

        obj = self.test_restaurant

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    # sanity check
    def test_unprivileged_user_with_restaurant_object(self):
        request = self.factory.delete('/')
        request.user = self.unprivileged_user

        obj = self.test_restaurant

        self.assertFalse(
            self.test_permission.has_object_permission(request, None, obj))

    def test_permitted_user_with_menu_object(self):
        request = self.factory.delete('/')
        request.user = self.permitted_user

        obj = self.test_menu

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_permitted_user_with_menusection_object(self):
        request = self.factory.delete('/')
        request.user = self.permitted_user

        obj = self.test_menusection

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_permitted_user_with_menuitem_object(self):
        request = self.factory.delete('/')
        request.user = self.permitted_user

        obj = self.test_menuitem

        self.assertTrue(
            self.test_permission.has_object_permission(request, None, obj))

    def test_non_restaurant_object(self):
        request = self.factory.delete('/')
        request.user = self.permitted_user

        obj = AnonymousUser

        with self.assertRaises(TypeError):
            self.test_permission.has_object_permission(request, None, obj)
