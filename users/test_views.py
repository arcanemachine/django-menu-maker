from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import html


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

        self.test_username = 'test_user'
        self.test_password = 'test_password'

        # get user count before POST
        old_user_count = get_user_model().objects.count()

        self.response = self.client.post(self.current_test_url, {
            'username': self.test_username,
            'password1': self.test_password,
            'password2': self.test_password})

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
