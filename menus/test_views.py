from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Menu
from restaurants.models import Restaurant

class MenuDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # create unprivileged user
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        # create restaurant admin user
        cls.restaurant_admin_user = \
            get_user_model().objects.create(username='restaurant_admin_user')
        cls.restaurant_admin_user.set_password('password')
        cls.restaurant_admin_user.save()

        # create test restaurant
        cls.test_restaurant = \
            Restaurant.objects.create(name='Test Restaurant')
        cls.test_restaurant.admin_users.add(cls.restaurant_admin_user)

        # create test menu
        cls.test_menu = Menu.objects.create(
                restaurant=cls.test_restaurant,
                name='Test Menu')

    def setUp(self):
        self.response = self.client.get(
            reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                }))
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')

    # view logic
    def test_get(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_type_is_DetailView(self):
        self.assertEqual(
            self.context['view'].__class__.__bases__[0].__name__, 'DetailView')

    def test_view_model_is_Menu(self):
        self.assertEqual(self.context['view'].model.__name__, 'Menu')

    def test_slug_url_kwarg_is_menu_slug(self):
        self.assertEqual(self.context['view'].slug_url_kwarg, 'menu_slug')

    # authentication
    def test_unauthenticated_user_cannot_view_link_to_add_section(self):
        self.assertNotIn('Add New Section', self.html)

    def test_unprivileged_user_cannot_view_link_to_add_section(self):
        self.client.login(
                username='test_user', password='password')
        self.setUp() # reload the page
        self.assertNotIn('Add New Section', self.html)

    def test_restaurant_admin_user_can_view_link_to_add_section(self):
        self.client.login(
                username='restaurant_admin_user', password='password')
        self.setUp() # reload the page
        self.assertIn('Add New Section', self.html)

    # no sections
    def test_menu_with_no_menu_sections(self):
        self.assertIn("This menu does not have any sections.", self.html)

    # TODO: 1 section
