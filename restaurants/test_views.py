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
        self.view = self.context['view']

    def test_view_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantListView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'ListView')

    def test_model(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    def test_context_object_name_is_restaurants(self):
        self.assertTrue('restaurants' in self.context)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)


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
            reverse('restaurants:restaurant_detail', kwargs={
                'restaurant_slug': self.test_restaurant.slug}))
        self.context = self.response.context
        self.view = self.context['view']

    # view attributes
    def test_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantDetailView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, "DetailView")

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # bad kwargs
    def test_bad_kwargs(self):
        self.response = self.client.get(
            reverse('restaurants:restaurant_detail', kwargs={
                'restaurant_slug': 'bad-slug'}))
        self.assertEqual(self.response.status_code, 404)
