from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection

class MenuModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.test_restaurant = \
            Restaurant.objects.create(name='Test Restaurant')

        cls.test_menu = Menu.objects.create(
                restaurant=cls.test_restaurant,
                name='Test Menu')

    def test_menu_content(self):

        expected_restaurant = self.test_restaurant
        expected_name = 'Test Menu'
        expected_slug = 'test-menu'

        self.assertEqual(self.test_menu.restaurant, expected_restaurant)
        self.assertEqual(self.test_menu.name, expected_name)
        self.assertEqual(self.test_menu.slug, expected_slug)

    ### VALIDATION ###

    def test_restaurant_cannot_have_two_menus_with_duplicate_name(self):
        with self.assertRaises(ValidationError):
            test_menu_2 = Menu.objects.create(
                    restaurant=self.test_restaurant,
                    name='Test Menu')

    def test_two_different_restaurants_can_have_same_menu_name(self):
        test_restaurant_2 = \
            Restaurant.objects.create(name="Test Restaurant 2")
        test_menu_2 = Menu.objects.create(
                restaurant=test_restaurant_2,
                name='Test Menu')
        self.assertEqual(Menu.objects.count(), 2)

    ### METHODS ###

    # __str__()
    def test_method___str___returns_name(self):
        expected_string = "Test Menu"
        self.assertEqual(str(self.test_menu), expected_string)

    # get_absolute_url()
    def test_method_get_absolute_url_returns_menu_detail(self):
        expected_url = reverse('menus:menu_detail',
                kwargs = {
                    'restaurant_slug': self.test_menu.restaurant.slug,
                    'menu_slug': self.test_menu.slug,
                    })

        self.assertEqual(self.test_menu.get_absolute_url(), expected_url)
