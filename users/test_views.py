from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

import html

from . import views


class UserLogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.current_test_url = reverse('users:logout')

        cls.test_user_username = 'test_user'
        cls.test_user_password = 'test_password'

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