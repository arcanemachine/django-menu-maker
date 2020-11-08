from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from factories import UserFactory
from menus_project import constants
from restaurants.models import Restaurant
from .serializers import RestaurantSerializer

test_user_password = constants.TEST_USER_PASSWORD
test_restaurant_name = constants.TEST_RESTAURANT_NAME

class RestaurantSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rest_client = APIClient()
        cls.serializer = RestaurantSerializer
        cls.test_user = UserFactory()

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'Restaurant')

    def test_meta_fields(self):
        self.assertEqual(self.serializer.Meta.fields,
            ['id', 'name', 'admin_users', 'menu_set'])

    def test_meta_read_only_fields(self):
        self.assertEqual(self.serializer.Meta.read_only_fields,
            ['admin_users', 'menu_set'])

    def test_new_object_adds_registrant_to_admin_users(self):
        self.current_test_url = reverse('api:restaurant_list_create')

        # create new restaurant
        self.rest_client.login(
            username=self.test_user.username,
            password=constants.TEST_USER_PASSWORD)
        self.response = self.rest_client.post(self.current_test_url, {
            'name': constants.TEST_RESTAURANT_NAME})

        # new restaurant created successfully
        self.assertEqual(self.response.status_code, 201)

        # get restaurant from pk
        self.test_restaurant = \
            Restaurant.objects.get(name=test_restaurant_name)

        # restaurant.admin_users contains only the registrant
        self.assertEqual(self.test_restaurant.admin_users.count(), 1)
        self.assertIn(self.test_user, self.test_restaurant.admin_users.all())
