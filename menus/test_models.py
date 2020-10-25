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

        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

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

    def test_field_restaurant_field_type(self):
        field_type = \
            self.test_menu._meta.get_field('restaurant').get_internal_type()
        self.assertEqual(field_type, 'ForeignKey')

    def test_field_restaurant_related_model(self):
        related_model = \
            self.test_menu._meta.get_field('restaurant').related_model.__name__
        self.assertEqual(related_model, 'Restaurant')
    
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

    def test_field_name_field_type(self):
        field_type = \
            self.test_menu._meta.get_field('name').get_internal_type()
        self.assertEqual(field_type, 'CharField')

    def test_field_name_max_length(self):
        max_length = self.test_menu._meta.get_field('name').max_length
        self.assertEqual(max_length, 128)

    def test_field_name_default(self):
        default = self.test_restaurant._meta.get_field('name').default
        self.assertEqual(default, None)

    def test_field_name_blank(self):
        blank = self.test_restaurant._meta.get_field('name').blank
        self.assertEqual(blank, False)


    # slug
    def test_field_slug_verbose_name(self):
        verbose_name = self.test_menu._meta.get_field('slug').verbose_name
        self.assertEqual(verbose_name, 'slug')

    def test_field_slug_field_type(self):
        field_type = \
            self.test_menu._meta.get_field('slug').get_internal_type()
        self.assertEqual(field_type, 'SlugField')

    def test_field_slug_max_length(self):
        slug_max_length = self.test_menu._meta.get_field('slug').max_length
        self.assertEqual(slug_max_length, 128)

    def test_field_slug_null(self):
        null = self.test_menu._meta.get_field('slug').null
        self.assertEqual(null, True)

    # theme
    def test_field_theme_choices_default(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(choices[0], ('default', "Default"))

    def test_field_theme_choices_secondary(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(choices[1], ('secondary', "Secondary"))

    def test_field_theme_verbose_name(self):
        verbose_name = self.test_menu._meta.get_field('theme').verbose_name
        self.assertEqual(verbose_name, 'theme')

    def test_field_theme_field_type(self):
        field_type = \
            self.test_menu._meta.get_field('theme').get_internal_type()
        self.assertEqual(field_type, 'CharField')

    def test_field_theme_max_length(self):
        max_length = self.test_menu._meta.get_field('theme').max_length
        self.assertEqual(max_length, 32)

    def test_field_theme_choices_is_THEME_CHOICES(self):
        choices = self.test_menu._meta.get_field('theme').choices
        self.assertEqual(self.test_menu.THEME_CHOICES, choices)

    def test_field_theme_default(self):
        default_choice = self.test_menu._meta.get_field('theme').default
        self.assertEqual(default_choice, 'default')


    ### META ###

    def test_meta_ordering(self):
        ordering = self.test_menu._meta.ordering
        self.assertEqual(ordering, ['name'])


    ### VALIDATION ###

    def test_validation_restaurant_cannot_have_two_menus_with_duplicate_slug(self):
        with self.assertRaises(ValidationError):
            self.test_restaurant.menu_set.create(name='Test Menu')
        with self.assertRaises(ValidationError):
            self.test_restaurant.menu_set.create(name='Test--Menu')

    def test_validation_two_different_restaurants_can_have_same_menu_slug(self):
        test_restaurant_2 = \
            Restaurant.objects.create(name="Test Restaurant 2")
        test_menu_2 = test_restaurant_2.menu_set.create(name='Test Menu')
        self.assertEqual(Menu.objects.count(), 2)

    ### METHODS ###

    # __str__()
    def test_method_str_returns_restaurant_name_and_menu_name(self):
        expected_string = "Test Restaurant - Test Menu"
        self.assertEqual(str(self.test_menu), expected_string)

    # get_absolute_url()
    def test_method_get_absolute_url_returns_menu_detail(self):
        expected_url = reverse('menus:menu_detail', kwargs = {
            'restaurant_slug': self.test_menu.restaurant.slug,
            'menu_slug': self.test_menu.slug })
        self.assertEqual(self.test_menu.get_absolute_url(), expected_url)

class MenuSectionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.test_restaurant = Restaurant.objects.create(name='Test Restaurant')
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')
        cls.test_menusection = cls.test_menu.menusection_set.create(
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

    ### FIELDS ###

    # menu
    def test_field_menu_verbose_name(self):
        verbose_name = \
            self.test_menusection._meta.get_field('menu').verbose_name
        self.assertEqual(verbose_name, 'menu')

    def test_field_menu_field_type(self):
        field_type = \
            self.test_menusection._meta.get_field('menu').get_internal_type()
        self.assertEqual(field_type, 'ForeignKey')

    def test_field_menu_related_model(self):
        related_model = self.test_menusection._meta.get_field('menu') \
            .related_model.__name__
        self.assertEqual(related_model, 'Menu')

    def test_field_menu_on_delete(self):
        on_delete = self.test_menusection._meta.get_field('menu') \
                .remote_field.on_delete
        self.assertTrue(on_delete is models.CASCADE)

    # name
    def test_field_name_verbose_name(self):
        verbose_name = \
            self.test_menusection._meta.get_field('name').verbose_name
        self.assertEqual(verbose_name, 'name')

    def test_field_name_field_type(self):
        field_type = \
            self.test_menusection._meta.get_field('name').get_internal_type()
        self.assertEqual(field_type, 'CharField')

    def test_field_name_max_length(self):
        max_length = self.test_menusection._meta.get_field('name').max_length
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
            self.test_menusection._meta.get_field('slug').verbose_name
        self.assertEqual(verbose_name, 'slug')

    def test_field_slug_field_type(self):
        field_type = \
            self.test_menusection._meta.get_field('slug').get_internal_type()
        self.assertEqual(field_type, 'SlugField')

    def test_field_slug_max_length(self):
        max_length = self.test_menusection._meta.get_field('slug').max_length
        self.assertEqual(max_length, 128)

    def test_field_slug_null(self):
        null = self.test_menusection._meta.get_field('slug').null
        self.assertEqual(null, True)

    ### VALIDATION ###

    def test_validation_menu_cannot_have_two_menusections_with_same_name(self):
        with self.assertRaises(ValidationError):
            self.test_menu.menusection_set.create(
                name=self.test_menusection.name)

    def test_validation_two_different_menus_can_have_same_menusection_slug(self):
        test_menu_2 = self.test_restaurant.menu_set.create(name='Test Menu 2')
        test_menu_2.menusection_set.create(name=self.test_menusection.name)
        self.assertEqual(MenuSection.objects.count(), 2)

    ### METHODS ###

    def test_method_str_returns_restaurant_name_and_menu_name_and_menusection_name(self):
        self.assertEqual(str(self.test_menusection),
            f"{self.test_menusection.menu.restaurant.name}: "\
                f"{self.test_menusection.menu.name} - "\
                    f"{self.test_menusection.name}")

    def test_method_get_absolute_url_returns_menusection_detail(self):
        expected_url = reverse('menus:menusection_detail', kwargs = {
            'restaurant_slug': self.test_menusection.menu.restaurant.slug,
            'menu_slug': self.test_menusection.menu.slug,
            'menusection_slug': self.test_menusection.slug,
            })
        self.assertEqual(
            self.test_menusection.get_absolute_url(), expected_url)
