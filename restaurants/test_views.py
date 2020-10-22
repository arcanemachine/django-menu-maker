from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Restaurant

class RestaurantListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # create test user
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = Restaurant.objects.create(name='Test Restaurant')
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

    def setUp(self):
        self.response = self.client.get(reverse('restaurants:restaurant_list'))
        self.context = self.response.context

    def test_get(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_type_is_ListView(self):
        self.assertEqual(
            self.context['view'].__class__.__bases__[0].__name__, "ListView")

    def test_context_object_name_is_restaurants(self):
        self.assertTrue('restaurants' in self.context)

    def test_context_object_type_is_Restaurant(self):
        self.assertEqual(self.context['view'].model.__name__, 'Restaurant')

class RestaurantDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # create test user
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = Restaurant.objects.create(name='Test Restaurant')
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

    def setUp(self):
        self.response = self.client.get(
            reverse('restaurants:restaurant_detail', 
                kwargs = {'restaurant_slug': self.test_restaurant.slug }))
        self.context = self.response.context

    def test_get(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_type_is_DetailView(self):
        self.assertEqual(
            self.context['view'].__class__.__bases__[0].__name__, "DetailView")

    def test_context_object_type_is_Restaurant(self):
        self.assertEqual(self.context['view'].model.__name__, 'Restaurant')
