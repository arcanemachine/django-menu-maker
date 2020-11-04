from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from .models import Restaurant
from menus_project import constants

test_user_username = constants.TEST_USER_USERNAME
test_user_password = constants.TEST_USER_PASSWORD
test_restaurant_name = constants.TEST_RESTAURANT_NAME

class RestaurantModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create test user
        cls.test_user = \
            get_user_model().objects.create(username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create test_restaurant
        cls.test_restaurant = \
            Restaurant.objects.create(name=test_restaurant_name)
        cls.test_restaurant.admin_users.add(cls.test_user)

    def test_object_name(self):
        self.assertEqual(self.test_restaurant._meta.object_name, 'Restaurant')

    def test_object_content(self):
        expected_name = test_restaurant_name
        expected_admin_users = \
            get_user_model().objects.filter(pk=self.test_user.pk)

        self.assertEqual(self.test_restaurant.name, expected_name)
        self.assertEqual(
            self.test_restaurant.slug, slugify(self.test_restaurant.name))
        self.assertEqual(
            set(self.test_restaurant.admin_users.all()),
            set(expected_admin_users))

    # FIELDS #

    # name
    def test_field_name_verbose_name(self):
        verbose_name = \
            self.test_restaurant._meta.get_field('name').verbose_name
        self.assertEqual(verbose_name, 'name')

    def test_field_name_field_type(self):
        field_type = \
            self.test_restaurant._meta.get_field('name').get_internal_type()
        self.assertEqual(field_type, 'CharField')

    def test_field_name_max_length(self):
        max_length = self.test_restaurant._meta.get_field('name').max_length
        self.assertEqual(max_length, 128)

    def test_field_name_default(self):
        default = self.test_restaurant._meta.get_field('name').default
        self.assertEqual(default, None)

    def test_field_name_blank(self):
        blank = self.test_restaurant._meta.get_field('name').blank
        self.assertEqual(blank, False)

    # slug
    def test_field_slug_verbose_name(self):
        verbose_name = \
            self.test_restaurant._meta.get_field('slug').verbose_name
        self.assertEqual(verbose_name, 'slug')

    def test_field_slug_field_type(self):
        field_type = \
            self.test_restaurant._meta.get_field('slug').get_internal_type()
        self.assertEqual(field_type, 'SlugField')

    def test_field_slug_max_length(self):
        max_length = self.test_restaurant._meta.get_field('slug').max_length
        self.assertEqual(max_length, 128)

    def test_field_slug_unique(self):
        is_unique = self.test_restaurant._meta.get_field('slug').unique
        self.assertEqual(is_unique, True)

    # slug
    def test_field_admin_users_verbose_name(self):
        verbose_name = \
            self.test_restaurant._meta.get_field('admin_users').verbose_name
        self.assertEqual(verbose_name, 'admin users')

    def test_field_admin_users_field_type(self):
        field_type = self.test_restaurant._meta.get_field('admin_users') \
            .get_internal_type()
        self.assertEqual(field_type, 'ManyToManyField')

    def test_field_admin_users_related_model(self):
        related_model = \
            self.test_restaurant._meta.get_field('admin_users').related_model
        self.assertEqual(related_model, get_user_model())

    # META #
    def test_meta_ordering(self):
        ordering = self.test_restaurant._meta.ordering
        self.assertEqual(ordering, ['name'])

    # VALIDATION #
    def test_validation_do_not_allow_slug_if_it_is_a_reserved_keyword(self):
        with self.assertRaises(ValidationError):
            Restaurant.objects.create(name='all')

    def test_validation_do_not_allow_duplicate_restaurant_slugs(self):
        with self.assertRaises(ValidationError):
            Restaurant.objects.create(name='Test Restaurant')

    # METHODS #
    def test_method_str(self):
        self.assertEqual(
            self.test_restaurant.__str__(), self.test_restaurant.name)

    def test_method_get_absolute_url(self):
        expected_url = reverse('restaurants:restaurant_detail', kwargs={
            'restaurant_slug': self.test_restaurant.slug})
        self.assertEqual(self.test_restaurant.get_absolute_url(), expected_url)
