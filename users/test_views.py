from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

from html import unescape
from urllib.parse import urlparse

from menus_project import constants as c
from menus_project import factories as f
from . import views


class RegisterViewTest(TestCase):

    def setUp(self):
        self.current_test_url = reverse('users:register')
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RegisterView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_form_class(self):
        self.assertEqual(self.view.form_class.__name__, 'NewUserCreationForm')

    def test_success_url(self):
        self.assertEqual(self.view.success_url, reverse('users:login'))

    def test_template_name(self):
        self.assertEqual(self.view.template_name, 'users/register.html')

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message,
            "Your account has been successfully registered.")

    # request.GET
    def test_request_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_request_post_method_register_new_user(self):
        # get user count before POST
        old_user_count = get_user_model().objects.count()

        self.response = self.client.post(self.current_test_url, {
            'username': c.TEST_USER_USERNAME,
            'email': c.TEST_USER_EMAIL,
            'password1': c.TEST_USER_PASSWORD,
            'password2': c.TEST_USER_PASSWORD,
            'captcha_0': 'test',
            'captcha_1': 'PASSED'})

        # user is redirected to users:login
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('users:login'))

        self.response = self.client.get(self.response.url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # template contains success_message
        self.assertIn(self.view.success_message, self.html)

        # user count increased by 1
        new_user_count = get_user_model().objects.count()
        self.assertEqual(old_user_count + 1, new_user_count)


class LoginViewTest(TestCase):

    def setUp(self):
        self.current_test_url = reverse('users:login')
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_name(self):
        self.assertTrue(self.view.template_name, 'users/login.html')


class PasswordChangeViewTest(TestCase):

    def setUp(self):
        self.test_user = f.UserFactory()

        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)

        self.current_test_url = reverse('users:password_change')
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_name(self):
        self.assertTrue(
            self.view.template_name, 'users/password_change_form.html')


class PasswordResetViewTest(TestCase):

    def setUp(self):
        self.current_test_url = reverse('users:password_reset')
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_name(self):
        self.assertTrue(
            self.view.template_name, 'users/password_reset_form.html')


class UserDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.restaurant_admin_user = f.UserFactory()

        cls.current_test_url = reverse('users:user_detail')

    def setUp(self):
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=c.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
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
        self.assertTemplateUsed(self.response, 'users/login.html')

    def test_get_method_authenticated_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, self.view.template_name)

    # TEMPLATE

    # template
    def test_template_shows_restaurants(self):
        test_restaurants = []

        # 0 restaurants
        self.assertIn("You have not registered any restaurants.", self.html)

        # 1 restaurant
        test_restaurants.append(
            f.RestaurantFactory(admin_users=[self.restaurant_admin_user]))
        self.client.get(self.current_test_url)
        self.response = self.client.get(self.current_test_url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{test_restaurants[0].name}", self.html)

        # 2 restaurants
        test_restaurants.append(
            f.RestaurantFactory(admin_users=[self.restaurant_admin_user]))
        self.client.get(self.current_test_url)
        self.response = self.client.get(self.current_test_url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{test_restaurants[0].name}", self.html)
        self.assertIn(f"{test_restaurants[1].name}", self.html)


class UserUpdateViewTest(TestCase):

    def setUp(self):
        self.test_user = f.UserFactory()
        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)

        self.current_test_url = reverse('users:user_update')
        self.response = self.client.get(self.current_test_url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'UserUpdateView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'UpdateView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'LoginRequiredMixin')

    def test_model(self):
        self.assertEqual(self.view.model, get_user_model())

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message,
            "You have updated your personal information.")

    # get_initial()
    def test_method_get_initial(self):
        self.assertEqual(
            self.view.get_initial(), {
                'first_name': self.test_user.first_name,
                'last_name': self.test_user.last_name,
                'email': self.test_user.email})

    # get_object()
    def test_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.test_user)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.client.logout()

        # request by unauthenticated user should redirect to login
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

    def test_get_method_authenticated_user(self):
        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)
        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_contains_proper_intro_text(self):
        self.assertIn(
            "Enter the details of your personal information here:", self.html)

    def test_template_form_contains_proper_initial_data_name(self):
        for key, value in self.view.get_initial().items():
            self.assertIn(rf'value="{value}"', self.html)

    # request.POST
    def test_request_post_method(self):
        updated_user_first_name = f"{self.test_user.first_name}y"
        updated_user_last_name = f"{self.test_user.last_name}son"

        # update self.test_user via POST
        self.response = self.client.post(self.current_test_url, {
            'first_name': updated_user_first_name,
            'last_name': updated_user_last_name,
            'email': self.test_user.email})
        self.html = unescape(self.response.content.decode('utf-8'))

        # user is redirected to users:user_detail
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('users:user_detail'))
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)

        # template contains updated user information
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{updated_user_first_name}", self.html)
        self.assertIn(f"{updated_user_last_name}", self.html)
        self.assertIn(f"{self.test_user.email}", self.html)


class UserDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.current_test_url = reverse('users:user_delete')

    def setUp(self):
        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)

        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'UserDeleteView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'DeleteView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'LoginRequiredMixin')

    def test_attribute_model(self):
        self.assertEqual(self.view.model, get_user_model())

    def test_attribute_template_name(self):
        self.assertEqual(
            self.view.template_name, 'users/user_confirm_delete.html')

    def test_attribute_success_message(self):
        self.assertEqual(
            self.view.success_message, "Your account has been deleted.")

    def test_attribute_success_url(self):
        self.assertEqual(self.view.get_success_url(), reverse('root'))

    # get_object()
    def test_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.test_user)

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, self.view.template_name)

    # template
    def test_get_method_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_contains_proper_confirm_text(self):
        self.assertIn(
            "Are you sure you want to delete your account?", self.html)

    # request.POST
    def test_request_post_method(self):
        # get user count before deleting self.test_user
        old_user_count = get_user_model().objects.count()

        # delete user via POST
        self.response = self.client.post(self.current_test_url)

        # user is redirected to homepage
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('root'))

        # homepage loads successfully and contains success_message
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("Your account has been deleted.", self.html)

        # object no longer exists
        with self.assertRaises(get_user_model().DoesNotExist):
            self.test_user.refresh_from_db()

        # user count decreased by 1
        new_user_count = get_user_model().objects.count()
        self.assertEqual(old_user_count - 1, new_user_count)


class UserLogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.current_test_url = reverse('users:logout')

    def setUp(self):
        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)

        # setup the view
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

    # request.GET
    def test_request_get_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 0)

    def test_request_get_method_authenticated_user(self):
        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 1)

    def test_request_post_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)
        self.assertEqual(len(self.response.context['messages']), 0)

    def test_request_post_method_authenticated_user(self):
        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # template contains 1 message
        self.assertEqual(len(self.response.context['messages']), 1)

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)
