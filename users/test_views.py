from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

import html

from urllib.parse import urlparse

from . import views
from restaurants.models import Restaurant
from menus.models import MenuSection

test_user_username = 'test_user'
test_user_password = 'test_user_password'
restaurant_admin_user_username = 'restaurant_admin'
restaurant_admin_user_password = 'restaurant_admin_password'
test_restaurant_name = 'Test Restaurant'
test_menu_name = 'Test Menu'
test_menusection_name = 'Test Menu Section'


class UserDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create unprivileged user
        cls.test_user = \
            get_user_model().objects.create(username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create restaurant admin user
        cls.restaurant_admin_user = get_user_model().objects.create(
            username=restaurant_admin_user_username)
        cls.restaurant_admin_user.set_password(restaurant_admin_user_password)
        cls.restaurant_admin_user.save()

        # create test restaurant
        cls.test_restaurants = []
        for i in range(2):
            cls.test_restaurants.append(
                Restaurant.objects.create(
                    name=f"{test_restaurant_name} {i+1}"))

        cls.current_test_url = reverse('users:user_detail')

    def setUp(self):
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=restaurant_admin_user_password)
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'UserDetailView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'DetailView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'LoginRequiredMixin')

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'User')

    # get_object()
    def test_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.restaurant_admin_user)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.get(self.current_test_url)

        # redirect to users:login
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertTrue(redirect_url, reverse('users:login'))
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'registration/login.html')

    def test_get_method_authenticated_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, self.view.template_name)

    # TEMPLATE

    # template
    def test_template_shows_restaurants(self):
        # 0 restaurants
        self.assertIn("You have not registered any restaurants.", self.html)

        # 1 restaurant
        self.test_restaurants[0].admin_users.add(self.restaurant_admin_user)
        self.client.get(self.current_test_url)
        self.response = self.client.get(self.current_test_url)
        self.html = html.unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{self.test_restaurants[0].name}", self.html)

        # 2 restaurants
        self.test_restaurants[1].admin_users.add(self.restaurant_admin_user)
        self.client.get(self.current_test_url)
        self.response = self.client.get(self.current_test_url)
        self.html = html.unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{self.test_restaurants[0].name}", self.html)
        self.assertIn(f"{self.test_restaurants[1].name}", self.html)

    # bad kwargs
    def test_bad_kwargs(self):
        for i in range(len(self.view.kwargs)):
            self.current_test_url = reverse('menus:menu_detail', kwargs={
                'restaurant_slug':
                    self.test_restaurant.slug if i != 0 else 'bad-slug',
                'menu_slug':
                    self.test_menu.slug if i != 1 else 'bad-slug'})
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)


class UserLogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.current_test_url = reverse('users:logout')

        cls.test_user_username = test_user_username
        cls.test_user_password = test_user_password

        cls.test_user = get_user_model().objects.create(
            username=cls.test_user_username)
        cls.test_user.set_password(cls.test_user_password)
        cls.test_user.save()

    def setUp(self):

        # login as test_user
        self.client.login(
            username=self.test_user_username, password=self.test_user_password)
        self.response = self.client.get(self.current_test_url)

        self.request = RequestFactory().get(self.current_test_url)
        self.request.user = self.test_user

        self.view = views.UserLogoutView()
        self.view.setup(self.request)

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'UserLogoutView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'LogoutView')

    def test_get_method_unauthenticated_user(self):

        self.client.logout()
        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 0)

    def test_get_method_authenticated_user(self):

        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 1)

    def test_post_method_unauthenticated_user(self):

        self.client.logout()
        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 0)

    def test_post_method_authenticated_user(self):

        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))

        # template contains 1 message
        self.assertEqual(len(self.response.context['messages']), 1)

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)


class RegisterViewTest(TestCase):

    def setUp(self):
        self.current_test_url = reverse('users:register')
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RegisterView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_form_class(self):
        self.assertEqual(self.view.form_class.__name__, 'UserCreationForm')

    def test_success_url(self):
        self.assertEqual(self.view.success_url, reverse('users:login'))

    def test_template_name(self):
        self.assertEqual(self.view.template_name, 'registration/register.html')

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message, "Account successfully registered")

    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_post_method_register_new_user(self):

        test_user_username = 'test_user'
        test_user_password = 'test_password'

        # get user count before POST
        old_user_count = get_user_model().objects.count()

        self.response = self.client.post(self.current_test_url, {
            'username': test_user_username,
            'password1': test_user_password,
            'password2': test_user_password})

        # user is redirected to users:login
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('users:login'))

        self.response = self.client.get(self.response.url)
        self.context = self.response.context
        self.html = html.unescape(self.response.content.decode('utf-8'))

        # template contains success_message
        self.assertIn(self.view.success_message, self.html)

        # user count increased by 1
        new_user_count = get_user_model().objects.count()
        self.assertEqual(old_user_count + 1, new_user_count)
