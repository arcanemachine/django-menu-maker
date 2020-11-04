from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from html import unescape

from .models import Restaurant

test_user_username = 'test_user'
test_user_password = 'test_user_password'
test_restaurant_name = 'Test Restaurant'

class RestaurantListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create test user
        cls.test_user = \
                get_user_model().objects.create(username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = \
            Restaurant.objects.create(name=test_restaurant_name)
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

        cls.current_test_url = reverse('restaurants:restaurant_list')

    def setUp(self):
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.view = self.context['view']

    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantListView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'ListView')

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
        cls.test_user = get_user_model().objects.create(
                username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = Restaurant.objects.create(
            name=test_restaurant_name)
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

        cls.current_test_url = reverse('restaurants:restaurant_detail',
            kwargs={'restaurant_slug': cls.test_restaurant.slug})

    def setUp(self):
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantDetailView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, "DetailView")

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_unauthorized_user_cannot_view_auth_links(self):
        self.assertNotIn('Add New Menu', self.html)

    def test_template_authorized_user_can_view_auth_links(self):
        self.client.login(
            username=self.test_user.username,
            password=test_user_password)
        self.setUp()
        self.assertIn('Add New Menu', self.html)


    # bad kwargs
    def test_bad_kwargs(self):
        self.response = self.client.get(
            reverse('restaurants:restaurant_detail', kwargs={
                'restaurant_slug': 'bad-slug'}))
        self.assertEqual(self.response.status_code, 404)
