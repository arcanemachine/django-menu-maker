from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from menus_project import constants as c
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class MenuModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_restaurant = \
            Restaurant.objects.create(name=c.TEST_RESTAURANT_NAME)
        cls.test_menu = \
            cls.test_restaurant.menu_set.create(name=c.TEST_MENU_NAME)

    def test_object_name(self):
        self.assertEqual(self.test_menu._meta.object_name, 'Menu')

    def test_object_content(self):
        expected_restaurant = self.test_restaurant
        expected_name = c.TEST_MENU_NAME
        expected_slug = slugify(expected_name)

        self.assertEqual(self.test_menu.restaurant, expected_restaurant)
        self.assertEqual(self.test_menu.name, expected_name)
        self.assertEqual(self.test_menu.slug, expected_slug)

    # FIELDS #

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
        default = self.test_menu._meta.get_field('name').default
        self.assertEqual(default, None)

    def test_field_name_blank(self):
        blank = self.test_menu._meta.get_field('name').blank
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

    # META #
    def test_meta_ordering(self):
        ordering = self.test_menu._meta.ordering
        self.assertEqual(ordering, ['name'])

    # VALIDATION #
    def test_validation_fail_restaurant_makes_two_menus_with_same_slug(self):
        with self.assertRaises(ValidationError):
            self.test_restaurant.menu_set.create(name=f"{self.test_menu.name}")

    def test_validation_do_not_allow_slug_if_it_is_a_reserved_keyword(self):
        with self.assertRaises(ValidationError):
            self.test_restaurant.menu_set.create(name='all')

    def test_validation_pass_two_restaurants_with_same_menu_slug(self):
        test_restaurant_2 = \
            Restaurant.objects.create(name=f"{self.test_restaurant.name} 2")
        test_restaurant_2.menu_set.create(name=self.test_menu.name)
        self.assertEqual(Menu.objects.count(), 2)

    # METHODS #
    def test_method_str_returns_restaurant_name_and_menu_name(self):
        expected_string = \
            f"{self.test_restaurant.name} - {self.test_menu.name}"
        self.assertEqual(str(self.test_menu), expected_string)

    def test_method_get_absolute_url(self):
        expected_url = reverse('menus:menu_detail', kwargs={
            'restaurant_slug': self.test_menu.restaurant.slug,
            'menu_slug': self.test_menu.slug})
        self.assertEqual(self.test_menu.get_absolute_url(), expected_url)


class MenuSectionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_restaurant = \
            Restaurant.objects.create(name=c.TEST_RESTAURANT_NAME)
        cls.test_menu = \
            cls.test_restaurant.menu_set.create(name=c.TEST_MENU_NAME)
        cls.test_menusection = cls.test_menu.menusection_set.create(
            name=c.TEST_MENUSECTION_NAME)

    def test_object_name(self):
        self.assertEqual(
                self.test_menusection._meta.object_name, 'MenuSection')

    def test_object_content(self):
        expected_menu = self.test_menu
        expected_name = self.test_menusection.name
        expected_slug = slugify(expected_name)

        self.assertEqual(self.test_menusection.menu, expected_menu)
        self.assertEqual(self.test_menusection.name, expected_name)
        self.assertEqual(self.test_menusection.slug, expected_slug)

    # FIELDS #

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
        default = self.test_menusection._meta.get_field('name').default
        self.assertEqual(default, None)

    def test_field_name_blank(self):
        blank = self.test_menusection._meta.get_field('name').blank
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

    # VALIDATION #
    def test_validation_fail_two_menusections_with_same_slug(self):
        with self.assertRaises(ValidationError):
            self.test_menu.menusection_set.create(
                name=self.test_menusection.name)

    def test_validation_do_not_allow_slug_if_it_is_a_reserved_keyword(self):
        with self.assertRaises(ValidationError):
            self.test_menu.menusection_set.create(name='all')

    def test_validation_pass_two_menus_with_same_menusection_slug(self):
        test_menu_2 = self.test_restaurant.menu_set.create(
            name=f'{self.test_menu.name} 2')
        test_menu_2.menusection_set.create(name=self.test_menusection.name)
        self.assertEqual(MenuSection.objects.count(), 2)

    # METHODS #
    def test_method_str(self):
        self.assertEqual(
            str(self.test_menusection),
            f"{self.test_menusection.menu.restaurant.name}: "
            f"{self.test_menusection.menu.name} - "
            f"{self.test_menusection.name}")

    def test_method_get_absolute_url(self):
        expected_url = reverse('menus:menusection_detail', kwargs={
            'restaurant_slug': self.test_menusection.menu.restaurant.slug,
            'menu_slug': self.test_menusection.menu.slug,
            'menusection_slug': self.test_menusection.slug})
        self.assertEqual(
            self.test_menusection.get_absolute_url(), expected_url)


class MenuItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_restaurant = \
            Restaurant.objects.create(name=c.TEST_RESTAURANT_NAME)
        cls.test_menu = \
            cls.test_restaurant.menu_set.create(name=c.TEST_MENU_NAME)
        cls.test_menusection = cls.test_menu.menusection_set.create(
            name=c.TEST_MENUSECTION_NAME)
        cls.test_menuitem = cls.test_menusection.menuitem_set.create(
            name=c.TEST_MENUITEM_NAME)

    def test_object_name(self):
        self.assertEqual(self.test_menuitem._meta.object_name, 'MenuItem')

    def test_object_content(self):
        expected_menusection = self.test_menusection
        expected_name = c.TEST_MENUITEM_NAME
        expected_slug = slugify(expected_name)

        self.assertEqual(self.test_menuitem.menusection, expected_menusection)
        self.assertEqual(self.test_menuitem.name, expected_name)
        self.assertEqual(self.test_menuitem.slug, expected_slug)

    # FIELDS #

    # menu
    def test_field_menusection_verbose_name(self):
        verbose_name = \
            self.test_menuitem._meta.get_field('menusection').verbose_name
        self.assertEqual(verbose_name, 'menusection')

    def test_field_menusection_field_type(self):
        field_type = self.test_menuitem._meta.get_field('menusection') \
                .get_internal_type()
        self.assertEqual(field_type, 'ForeignKey')

    def test_field_menusection_related_model(self):
        related_model = self.test_menuitem._meta.get_field('menusection') \
            .related_model.__name__
        self.assertEqual(related_model, 'MenuSection')

    def test_field_menusection_on_delete(self):
        on_delete = self.test_menuitem._meta.get_field('menusection') \
            .remote_field.on_delete
        self.assertTrue(on_delete is models.CASCADE)

    # name
    def test_field_name_verbose_name(self):
        verbose_name = \
            self.test_menuitem._meta.get_field('name').verbose_name
        self.assertEqual(verbose_name, 'name')

    def test_field_name_field_type(self):
        field_type = \
            self.test_menuitem._meta.get_field('name').get_internal_type()
        self.assertEqual(field_type, 'CharField')

    def test_field_name_max_length(self):
        max_length = self.test_menuitem._meta.get_field('name').max_length
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
            self.test_menuitem._meta.get_field('slug').verbose_name
        self.assertEqual(verbose_name, 'slug')

    def test_field_slug_field_type(self):
        field_type = \
            self.test_menuitem._meta.get_field('slug').get_internal_type()
        self.assertEqual(field_type, 'SlugField')

    def test_field_slug_max_length(self):
        max_length = self.test_menuitem._meta.get_field('slug').max_length
        self.assertEqual(max_length, 128)

    # VALIDATION #
    def test_validation_fail_two_menuitems_with_same_slug(self):
        with self.assertRaises(ValidationError):
            self.test_menusection.menuitem_set.create(
                name=self.test_menuitem.name)

    def test_validation_do_not_allow_slug_if_it_is_a_reserved_keyword(self):
        with self.assertRaises(ValidationError):
            self.test_menusection.menuitem_set.create(name='all')

    def test_validation_pass_two_menusections_with_same_menuitem_slug(self):
        test_menusection_2 = self.test_menu.menusection_set.create(
            name='{self.test_menusection.name} 2')
        test_menusection_2.menuitem_set.create(name=self.test_menuitem.name)
        self.assertEqual(MenuItem.objects.count(), 2)

    # METHODS #
    def test_method_str(self):
        self.assertEqual(
            str(self.test_menuitem),
            f"{self.test_menuitem.menusection.menu.restaurant.name}: "
            f"{self.test_menuitem.menusection.menu.name} - "
            f"{self.test_menuitem.menusection.name} - "
            f"{self.test_menuitem.name}")

    def test_method_get_absolute_url(self):
        expected_url = reverse('menus:menuitem_detail', kwargs={
            'restaurant_slug':
                self.test_menuitem.menusection.menu.restaurant.slug,
            'menu_slug': self.test_menuitem.menusection.menu.slug,
            'menusection_slug': self.test_menuitem.menusection.slug,
            'menuitem_slug': self.test_menuitem.slug})
        self.assertEqual(
            self.test_menuitem.get_absolute_url(), expected_url)
