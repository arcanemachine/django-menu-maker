from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Restaurant

class RestaurantModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):

        # create test user
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        # create test_restaurant
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

    ### FIELDS ###

    # name
    def test_field_name_attname(self):
        attname = self.test_restaurant._meta.get_field('name').attname
        self.assertEqual(attname, 'name')

    def test_field_name_is_CharField(self):
        internal_type = \
            self.test_restaurant._meta.get_field('name').get_internal_type()
        self.assertEqual(internal_type, 'CharField')

    def test_field_name_max_length(self):
        max_length = self.test_restaurant._meta.get_field('name').max_length
        self.assertEqual(max_length, 128)

    # slug
    def test_field_slug_attname(self):
        attname = self.test_restaurant._meta.get_field('slug').attname
        self.assertEqual(attname, 'slug')

    def test_field_slug_is_SlugField(self):
        internal_type = \
            self.test_restaurant._meta.get_field('slug').get_internal_type()
        self.assertEqual(internal_type, 'SlugField')

    def test_field_slug_max_length(self):
        max_length = self.test_restaurant._meta.get_field('slug').max_length
        self.assertEqual(max_length, 128)

    def test_field_slug_unique(self):
        is_unique = self.test_restaurant._meta.get_field('slug').unique
        self.assertEqual(is_unique, True)

    def test_field_slug_null(self):
        is_null = self.test_restaurant._meta.get_field('slug').null
        self.assertEqual(is_null, True)

    # slug
    def test_field_admin_users_attname(self):
        attname = self.test_restaurant._meta.get_field('admin_users').attname
        self.assertEqual(attname, 'admin_users')

    def test_field_admin_users_is_ManyToManyField(self):
        internal_type = self.test_restaurant._meta.get_field('admin_users') \
            .get_internal_type()
        self.assertEqual(internal_type, 'ManyToManyField')

    def test_field_admin_users_uses_settings_AUTH_USER_MODEL(self):
        related_model = \
            self.test_restaurant._meta.get_field('admin_users').related_model
        self.assertEqual(related_model, get_user_model())

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
