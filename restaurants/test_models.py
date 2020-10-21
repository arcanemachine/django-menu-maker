from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Restaurant

class RestaurantModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        cls.test_restaurant = Restaurant.objects.create(
            name='Test Restaurant')
        cls.test_restaurant.admin_users.add(cls.test_user)

    def test_restaurant_object_content(self):
        expected_name = 'Test Restaurant'
        expected_slug = 'test-restaurant'
        expected_admin_users = \
            get_user_model().objects.filter(pk=self.test_user.pk)

        self.assertEqual(self.test_restaurant.name, expected_name)
        self.assertEqual(self.test_restaurant.slug, expected_slug)
        self.assertEqual(
            set(self.test_restaurant.admin_users.all()),
            set(expected_admin_users))

    ### VALIDATION ###

    def test_do_not_allow_duplicate_restaurant_slugs(self):
        with self.assertRaises(ValidationError):
            test_restaurant_2 = Restaurant.objects.create(
                    name='Test Restaurant')

    ### METHODS ###

    def test_method___str___returns_restaurant_name(self):
        self.assertEqual(str(self.test_restaurant), self.test_restaurant.name)

    def test_method_get_absolute_url_returns_restaurant_detail(self):
        expected_url = reverse('restaurants:restaurant_detail',
            kwargs = {'restaurant_slug': self.test_restaurant.slug})
        self.assertEqual(self.test_restaurant.get_absolute_url(), expected_url)
