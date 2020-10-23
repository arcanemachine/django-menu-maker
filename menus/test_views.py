from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from urllib.parse import urlparse

from .models import Menu, MenuSection
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
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

    def setUp(self):
        self.current_test_url = reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')

    # view logic
    def test_view_type_is_DetailView(self):
        self.assertEqual(
            self.context['view'].__class__.__bases__[0].__name__, 'DetailView')

    def test_view_model_is_Menu(self):
        self.assertEqual(self.context['view'].model.__name__, 'Menu')

    def test_slug_url_kwarg_is_menu_slug(self):
        self.assertEqual(self.context['view'].slug_url_kwarg, 'menu_slug')

    # authentication
    def test_get(self):
        # page should load for all users
        self.assertEqual(self.response.status_code, 200)

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

    # number of menusections
    def test_menu_with_no_menusections(self):
        self.assertIn("This menu does not have any sections.", self.html)
        self.assertEqual(MenuSection.objects.count(), 0)

    def test_menu_with_1_menusection(self):
        test_menusection = \
                self.test_menu.menusection_set.create(name='Test Menu Section')
        self.assertEqual(MenuSection.objects.count(), 1)

        self.setUp() # reload the page
        self.assertIn(test_menusection.name, self.html)

    def test_menu_with_1_menusection(self):
        test_menusection_1 = self.test_menu.menusection_set.create(
                name='Test Menu Section 1')
        test_menusection_2 = self.test_menu.menusection_set.create(
                name='Test Menu Section 2')
        self.assertEqual(MenuSection.objects.count(), 2)

        self.setUp() # reload the page
        self.assertIn(test_menusection_1.name, self.html)
        self.assertIn(test_menusection_2.name, self.html)

class MenuSectionCreateViewTest(TestCase):

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
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

    def setUp(self):

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menusection_create',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view parameters
    def test_view_name_is_MenuSectionCreateView(self):
        self.assertEqual(
            self.view.__class__.__name__, 'MenuSectionCreateView')

    def test_view_type_is_CreateView(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_view_model(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuSection')

    def test_view_fields(self):
        self.assertEqual(self.context['view'].fields, ['name'])

    def test_view_template_name(self):
        self.assertEqual(self.context['view'].template_name,
                'menus/menusection_create.html')

    # get_context_data
    def test_view_context_contains_menu(self):
        self.assertTrue('menu' in self.context)

    def test_view_context_contains_correct_menu(self):
        self.assertEqual(self.context['menu'], self.test_menu)

    # authentication - unauthorized user
    def test_view_get_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.get(self.current_test_url, follow=True)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'registration/login.html')

    def test_view_get_method_authenticated_but_unauthorized_user(self):
        self.client.login(
                username='test_user', password='password')
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')

        self.assertEqual(self.response.status_code, 403)

    def test_view_post_method_unauthenticated_user(self):
        self.client.logout()

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # attempt to create new menusection via POST
        self.response = self.client.post(self.current_test_url,
                kwargs = {'name': 'Test Menu Section'})

        # new menusection count should be the same as before
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count, new_menusection_count)

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)

        # URL must be parsed to account for GET parameters
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

    # authentication - authorized user

    def test_view_get_method_authorized_user(self):
        pass

    def test_view_post_method_authorized_user(self):

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # create new menusection via POST
        self.response = self.client.post(self.current_test_url,
                kwargs = {'name': 'Test Menu Section'})

        # menusection object count increased by 1
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count, new_menusection_count)

