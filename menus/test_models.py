from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection

class MenuModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.test_restaurant = Restaurant.objects.create(name='Test Restaurant')

        cls.test_menu = Menu.objects.create(
            restaurant=cls.test_restaurant,
            name='Test Menu')

    def test_menu_object_name(self): 
        self.assertEqual(self.test_menu._meta.object_name, 'Menu')

    def test_menu_object_content(self):

        expected_restaurant = self.test_restaurant
        expected_name = 'Test Menu'
        expected_slug = 'test-menu'

        self.assertEqual(self.test_menu.restaurant, expected_restaurant)
        self.assertEqual(self.test_menu.name, expected_name)
        self.assertEqual(self.test_menu.slug, expected_slug)

    ### FIELDS ###

    # restaurant
    def test_field_restaurant_verbose_name(self):
        verbose_name = \
            self.test_menu._meta.get_field('restaurant').verbose_name
        self.assertEqual(verbose_name, 'restaurant')
    
    def test_field_restaurant_on_delete(self):
        on_delete = \
            self.test_menu._meta.get_field('restaurant').remote_field.on_delete
        self.assertTrue(on_delete is models.CASCADE)

    def test_field_restaurant_null(self):
        null = self.test_menu._meta.get_field('restaurant').null
        self.assertEqual(null, True)

    # name
    def test_field_name_verbose_name(self):
        verbose_name = self.test_menu._meta.get_field('name').verbose_name
        self.assertEqual(verbose_name, 'name')

    def test_field_name_max_length(self):
        max_length = self.test_menu._meta.get_field('name').max_length
        self.assertEqual(max_length, 128)

    # slug
    def test_field_slug_verbose_name(self):
        verbose_name = self.test_menu._meta.get_field('slug').verbose_name
        self.assertEqual(verbose_name, 'slug')

    def test_field_slug_max_length(self):
        slug_max_length = self.test_menu._meta.get_field('slug').max_length
        self.assertEqual(slug_max_length, 128)

    # theme
    def test_field_theme_choices_is_THEME_CHOICES(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(self.test_menu.THEME_CHOICES, choices)

    def test_field_theme_choices_default(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(choices[0], ('default', "Default"))

    def test_field_theme_choices_secondary(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(choices[1], ('secondary', "Secondary"))

    def test_field_theme_verbose_name(self):
        verbose_name = self.test_menu._meta.get_field('theme').verbose_name
        self.assertEqual(verbose_name, 'theme')

    def test_field_theme_max_length(self):
        max_length = self.test_menu._meta.get_field('theme').max_length
        self.assertEqual(max_length, 32)

    def test_field_theme_default(self):
        default_choice = self.test_menu._meta.get_field('theme').default
        self.assertEqual(default_choice, 'default')


    ### META ###

    def test_meta_ordering(self):
        ordering = self.test_menu._meta.ordering
        self.assertEqual(ordering, ['name'])


    ### VALIDATION ###

    def test_validation_restaurant_cannot_have_two_menus_with_duplicate_name(self):
        with self.assertRaises(ValidationError):
            test_menu_2 = Menu.objects.create(
                restaurant=self.test_restaurant,
                name='Test Menu')

    def test_validation_two_different_restaurants_can_have_same_menu_name(self):
        test_restaurant_2 = \
            Restaurant.objects.create(name="Test Restaurant 2")
        test_menu_2 = Menu.objects.create(
            restaurant=test_restaurant_2,
            name='Test Menu')
        self.assertEqual(Menu.objects.count(), 2)

    ### METHODS ###

    # __str__()
    def test_method___str___returns_menu_name(self):
        expected_string = "Test Menu"
        self.assertEqual(str(self.test_menu), expected_string)

    # get_absolute_url()
    def test_method_get_absolute_url_returns_menu_detail(self):
        expected_url = reverse('menus:menu_detail',
                kwargs = {
                    'restaurant_slug': self.test_menu.restaurant.slug,
                    'menu_slug': self.test_menu.slug })
        self.assertEqual(self.test_menu.get_absolute_url(), expected_url)

class MenuSectionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.test_restaurant = Restaurant.objects.create(name='Test Restaurant')

        cls.test_menu = Menu.objects.create(
            restaurant=cls.test_restaurant,
            name='Test Menu')

        cls.test_menusection = MenuSection.objects.create(
            menu=cls.test_menu,
            name='Test Menu Section')

    def test_menusection_object_name(self):
        self.assertEqual(
                self.test_menusection._meta.object_name, 'MenuSection')
    
    def test_menusection_object_content(self):

        expected_menu = self.test_menu
        expected_name = 'Test Menu Section'
        expected_slug = 'test-menu-section'

        self.assertEqual(self.test_menusection.menu, self.test_menu)
        self.assertEqual(self.test_menusection.name, expected_name)
        self.assertEqual(self.test_menusection.slug, expected_slug)

