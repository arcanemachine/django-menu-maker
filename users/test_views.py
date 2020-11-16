from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from html import unescape
from urllib.parse import urlparse

from menus_project import constants as c
from menus_project import factories as f
from . import views
from .forms import NewUserCreationForm

UserModel = get_user_model()


class RegisterViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authenticated_user = f.UserFactory(username='authenticated_user')

        cls.current_test_url = reverse('users:register')
        cls.next_url = reverse('restaurants:restaurant_list')

    def setUp(self):
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

    def test_template_name(self):
        self.assertEqual(self.view.template_name, 'users/register.html')

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message, c.USER_REGISTER_SUCCESS_MESSAGE)

    # methods
    def test_get_form_kwargs(self):
        kwargs = self.view.get_form_kwargs()
        self.assertIn('next_url', kwargs)
        self.assertEqual(kwargs['next_url'], None)

    def test_get_form_kwargs_with_next_url(self):
        self.current_test_url = f"{self.current_test_url}?next={self.next_url}"
        self.setUp()

        kwargs = self.view.get_form_kwargs()
        self.assertIn('next_url', kwargs)
        self.assertEqual(kwargs['next_url'], self.next_url)

    # success_url
    def test_success_url_with_next_kwarg(self):
        self.current_test_url = \
            self.current_test_url + '?next=' + self.next_url
        self.setUp()
        self.assertEqual(self.view.get_success_url(), self.next_url)

    def test_success_url_with_authenticated_user(self):
        """This test is handled in the request.GET tests."""
        pass

    def test_success_url_if_email_confirmation_required(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            self.assertEqual(self.view.get_success_url(), reverse('root'))

    def test_success_url_if_email_confirmation_not_required(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=False):
            self.assertEqual(
                self.view.get_success_url(), reverse(settings.LOGIN_URL))

    # request.GET
    def test_request_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    def test_request_get_method_authenticated_user(self):
        self.client.login(
            username=self.authenticated_user, password=c.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)

        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

    def test_request_get_method_authenticated_user_with_get_kwarg_next(self):
        self.client.login(
            username=self.authenticated_user, password=c.TEST_USER_PASSWORD)
        self.response = \
            self.client.get(self.current_test_url + '?next=' + self.next_url)

        # redirects to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, self.next_url)

        # template contains c.USER_REGISTER_ALREADY_AUTHENTICATED_MESSAGE
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_REGISTER_ALREADY_AUTHENTICATED_MESSAGE, self.html)

    # request.POST
    def test_request_post_method_new_user_no_confirmation_required(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=False):
            # get user count before POST
            old_user_count = UserModel.objects.count()

            self.response = self.client.post(self.current_test_url, {
                'username': c.TEST_USER_USERNAME,
                'email': c.TEST_USER_EMAIL,
                'password1': c.TEST_USER_PASSWORD,
                'password2': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})

            # user is redirected to success_url
            self.assertEqual(self.response.status_code, 302)
            self.assertEqual(self.response.url, self.view.get_success_url())

            self.response = self.client.get(self.response.url)
            self.context = self.response.context
            self.html = unescape(self.response.content.decode('utf-8'))

            # template contains success_message
            self.assertIn(self.view.success_message, self.html)

            # user count increased by 1
            new_user_count = UserModel.objects.count()
            self.assertEqual(old_user_count + 1, new_user_count)

            # new user can log in immediately
            new_user = UserModel.objects.get(username=c.TEST_USER_USERNAME)
            self.assertTrue(new_user.is_active)

            # welcome email sent
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Welcome to", mail.outbox[0].subject)
            self.assertIn("You can login to your account", mail.outbox[0].body)

    def test_request_post_method_register_user_confirmation_required(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # get user count before POST
            old_user_count = UserModel.objects.count()

            self.response = self.client.post(self.current_test_url, {
                'username': c.TEST_USER_USERNAME,
                'email': c.TEST_USER_EMAIL,
                'password1': c.TEST_USER_PASSWORD,
                'password2': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})

            # user is redirected to success_url
            self.assertEqual(self.response.status_code, 302)
            self.assertEqual(self.response.url, reverse('root'))

            self.response = self.client.get(self.response.url)
            self.context = self.response.context
            self.html = unescape(self.response.content.decode('utf-8'))

            # template contains success_message
            self.assertIn(self.view.success_message, self.html)

            # user count increased by 1
            new_user_count = UserModel.objects.count()
            self.assertEqual(old_user_count + 1, new_user_count)

            # new user still requires confirmation
            new_user = UserModel.objects.get(username=c.TEST_USER_USERNAME)
            self.assertFalse(new_user.is_active)

            # confirmation email sent
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Confirm your account", mail.outbox[0].subject)
            self.assertIn("confirm your account", mail.outbox[0].body)


class EmailConfirmationViewTest(TestCase):

    def setUp(self):
        self.authenticated_user = f.UserFactory(username='authenticated_user')

        self.form_instance = NewUserCreationForm()
        self.test_uid = self.form_instance.send_new_user_email(
            self.authenticated_user, get_uid=True)
        self.test_token = self.form_instance.send_new_user_email(
            self.authenticated_user, get_token=True)

        self.current_test_url = reverse('users:user_activation', kwargs={
            'uidb64': self.test_uid,
            'token': self.test_token})
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # helper functions
    def setup_unconfirmed_user(
            self, username, registration_url=reverse('users:register'),
            next_url=None):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            self.response = self.client.post(registration_url, {
                'username': username,
                'email': c.TEST_USER_EMAIL,
                'password1': c.TEST_USER_PASSWORD,
                'password2': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})
            user = UserModel.objects.get(username=username)
            self.uid = \
                self.form_instance.send_new_user_email(user, get_uid=True)
            self.token = \
                self.form_instance.send_new_user_email(user, get_token=True)
            self.current_test_url = \
                self.form_instance.send_new_user_email(
                    user, get_path=True, next_url=next_url)
            return user

    def user_activation_post_data(
            self, url=None, username=c.TEST_USER_USERNAME,
            password=c.TEST_USER_PASSWORD, captcha='PASSED'):
        if url is None:
            url = self.current_test_url
        return self.client.post(url, {
                                'username': username,
                                'password': password,
                                'captcha_0': 'test',
                                'captcha_1': captcha})

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'UserActivationView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'UserLoginView')

    # view methods
    def test_get_method_displays_USER_ACTIVATION_VIEW_MESSAGE(self):
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_ACTIVATION_VIEW_MESSAGE, self.html)

    def test_get_form_kwargs(self):
        kwargs = self.view.get_form_kwargs()
        self.assertIn('user_pk', kwargs)
        self.assertEqual(kwargs['user_pk'], self.authenticated_user.pk)
        self.assertIn('token', kwargs)
        self.assertTrue(default_token_generator.check_token(
            self.authenticated_user, kwargs['token']))

    def test_form_valid_and_not_token_is_valid_ie_already_active_user(self):
        # covered by test_active_user_uses_activation_view_to_log_in
        pass

    def test_form_valid_and_token_is_valid_ie_successful_user_activation(self):
        # covered by test_successful_activation
        pass

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # functional tests
    def test_active_user_uses_activation_view_to_log_in(self):
        active_user = f.UserFactory()
        self.client.login(username=active_user, password=c.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        # user has successfully logged in
        self.assertEqual(self.response.wsgi_request.user, active_user)

        # user is redirected and template contains
        # c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE, self.html)

    def test_token_is_valid(self):
        self.assertTrue(default_token_generator.check_token(
            self.authenticated_user, self.test_token))

    def test_successful_activation(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # register user
            unconfirmed_user = \
                self.setup_unconfirmed_user(username='unconfirmed_user')

            # check that user is unconfirmed
            self.assertFalse(unconfirmed_user.is_active)

            # email is sent
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Confirm your account", mail.outbox[0].subject)
            self.assertIn("confirm your account", mail.outbox[0].body)

            # client goes to url in email
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, 'users/login.html')

            # template contains c.USER_ACTIVATION_VIEW_MESSAGE
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_VIEW_MESSAGE, self.html)

            # user posts login info into user_activation
            self.response = \
                self.user_activation_post_data(username='unconfirmed_user')
            self.assertEqual(self.response.status_code, 302)
            self.assertEqual(
                self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

            # template contains success_message
            self.response = self.client.get(self.response.url)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_SUCCESS_MESSAGE, self.html)

            # user is active and logged in
            unconfirmed_user.refresh_from_db()
            self.assertEqual(self.response.wsgi_request.user, unconfirmed_user)
            self.assertTrue(unconfirmed_user.is_active)

    def test_successful_activation_with_next_kwarg(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            next_url = reverse('restaurants:restaurant_list')
            registration_url_with_next_kwarg = \
                reverse('users:register') + f'?next={next_url}'

            # register user
            unconfirmed_user = \
                self.setup_unconfirmed_user(
                    username='unconfirmed_user',
                    registration_url=registration_url_with_next_kwarg,
                    next_url=next_url)

            # check that user is unconfirmed
            self.assertFalse(unconfirmed_user.is_active)

            # email is sent
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Confirm your account", mail.outbox[0].subject)
            self.assertIn("confirm your account", mail.outbox[0].body)

            # email contains next_url
            self.assertIn(f'?next={next_url}', mail.outbox[0].body)

            # client goes to url in email
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, 'users/login.html')

            # template contains c.USER_ACTIVATION_VIEW_MESSAGE
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_VIEW_MESSAGE, self.html)

            # user posts login info into user_activation
            self.response = \
                self.user_activation_post_data(username='unconfirmed_user')
            self.assertEqual(self.response.status_code, 302)

            # user is redirected to next_url
            self.assertEqual(self.response.url, next_url)

            # view uses proper template
            self.response = self.client.get(self.response.url)
            self.assertTemplateUsed(
                self.response, 'restaurants/restaurant_list.html')

            # view contains success_message
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_SUCCESS_MESSAGE, self.html)

            # user is active and logged in
            unconfirmed_user.refresh_from_db()
            self.assertEqual(self.response.wsgi_request.user, unconfirmed_user)
            self.assertTrue(unconfirmed_user.is_active)

    def test_user_does_successful_activation_twice(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            self.test_successful_activation()
            self.client.logout()

            # get the unconfirmed user object from the previous test
            unconfirmed_user = \
                UserModel.objects.get(username='unconfirmed_user')

            # user posts login info into user_activation
            self.response = \
                self.user_activation_post_data(username='unconfirmed_user')
            self.assertEqual(self.response.status_code, 302)
            self.assertEqual(
                self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

            # user is logged in, nothing changes despite using activation view
            self.assertEqual(self.response.wsgi_request.user, unconfirmed_user)
            self.response = self.client.get(self.response.url)
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, 'users/user_detail.html')

            # template contains c.USER_LOGIN_SUCCESS_MESSAGE
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_LOGIN_SUCCESS_MESSAGE, self.html)

    def test_wrong_password_unconfirmed_user(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # register user
            unconfirmed_user = \
                self.setup_unconfirmed_user(username='unconfirmed_user')

            # user attempts to log in to user_activation
            self.response = \
                self.user_activation_post_data(
                    username='unconfirmed_user', password='wrong_password')
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(
                "Please enter a correct username and password.", self.html)

            # user is still unconfirmed and not logged in
            unconfirmed_user.refresh_from_db()
            self.assertFalse(self.response.wsgi_request.user.is_authenticated)
            self.assertFalse(unconfirmed_user.is_active)

    def test_wrong_captcha(self):
        """
        Previous form validation code would check the user's credentials
        even if the form had errors in it, leading to the possibility
        of automated credential checking, since this meant that the captcha
        did not need to be completed to check the credentials.

        This test ensures that the credentials are not checked if the form
        has other errors in it.
        """
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # register user
            unconfirmed_user = \
                self.setup_unconfirmed_user(username='unconfirmed_user')

            # user attempts to activate account
            # but uses wrong password and captcha
            self.response = \
                self.user_activation_post_data(
                    username='unconfirmed_user',
                    password='wrong_password',
                    captcha='wrong_captcha')
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(
                "Please enter a correct username and password", self.html)

            # user tries again but gets only the captcha wrong
            self.response = \
                self.user_activation_post_data(
                    username='unconfirmed_user', captcha='wrong_captcha')
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))

            # template does not leak successful user authentication details
            self.assertNotIn(c.USER_IS_UNCONFIRMED_MESSAGE, self.html)
            self.assertIn("Invalid CAPTCHA", self.html)

            # user is still unconfirmed and not logged in
            unconfirmed_user.refresh_from_db()
            self.assertFalse(unconfirmed_user.is_active)
            self.assertFalse(self.response.wsgi_request.user.is_authenticated)

    # test banned user with good url
    def test_banned_user_with_valid_url(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # create banned user
            banned_user = f.UserFactory(
                is_active=False, last_login=timezone.now())

            # generate welcome email url
            self.current_test_url = self.form_instance.send_new_user_email(
                banned_user, get_path=True)

            # attempt to activate account
            self.response = self.user_activation_post_data(
                username=banned_user.username)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(
                "Please enter a correct username and password.", self.html)

            # user is still banned
            banned_user.refresh_from_db()
            self.assertFalse(banned_user.is_active)

            # sanity check - unban the user, allow them to log in
            banned_user.is_active = True
            banned_user.save()
            self.response = \
                self.user_activation_post_data(username=banned_user.username)
            self.assertEqual(self.response.status_code, 302)
            self.assertEqual(self.response.wsgi_request.user, banned_user)

    # bad url parameters
    def test_uid_for_wrong_user(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # create unconfirmed user
            unconfirmed_user = self.setup_unconfirmed_user('unconfirmed_user')

            # generate bad url
            other_user_uid = self.form_instance.send_new_user_email(
                self.authenticated_user, get_uid=True)
            good_token = self.token
            self.current_test_url = reverse('users:user_activation', kwargs={
                'uidb64': other_user_uid,
                'token': good_token})

            # attempt to activate account
            self.response = self.user_activation_post_data(
                username=unconfirmed_user.username)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_INVALID_URL_MESSAGE, self.html)

            # user is still unactivated
            unconfirmed_user.refresh_from_db()
            self.assertFalse(unconfirmed_user.is_active)

    def test_bad_undecodable_uid(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # generate bad url
            bad_uid = '5'
            good_token = self.test_token
            self.current_test_url = reverse('users:user_activation', kwargs={
                'uidb64': bad_uid,
                'token': good_token})

            # attempt to access activation url
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

    def test_token_for_wrong_user(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # create unconfirmed user
            unconfirmed_user = self.setup_unconfirmed_user('unconfirmed_user')

            # generate bad url
            good_uid = self.uid
            other_user_token = self.form_instance.send_new_user_email(
                self.authenticated_user, get_token=True)
            self.current_test_url = reverse('users:user_activation', kwargs={
                'uidb64': good_uid,
                'token': other_user_token})

            # attempt to activate account
            self.response = self.user_activation_post_data(
                username=unconfirmed_user.username)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_INVALID_URL_MESSAGE, self.html)

            # user is still unactivated
            unconfirmed_user.refresh_from_db()
            self.assertFalse(unconfirmed_user.is_active)

    def test_url_for_wrong_user(self):
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            other_user_activation_url = self.current_test_url

            # register new user
            suspicious_user = self.setup_unconfirmed_user('unconfirmed_user')

            # attempt to activate account using other user activation url
            self.response = self.user_activation_post_data(
                username=suspicious_user.username,
                url=other_user_activation_url)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_INVALID_URL_MESSAGE, self.html)

            # user is still unactivated
            suspicious_user.refresh_from_db()
            self.assertFalse(suspicious_user.is_active)


class UserLoginViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.current_test_url = reverse('users:login')
        cls.next_url = reverse('restaurants:restaurant_list')

    def setUp(self):
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'UserLoginView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'LoginView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'SuccessMessageMixin')

    def test_form_class(self):
        self.assertEqual(
            self.view.form_class.__name__, 'UserAuthenticationForm')

    def test_template_name(self):
        self.assertEqual(self.view.template_name, 'users/login.html')

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message, c.USER_LOGIN_SUCCESS_MESSAGE)

    # methods
    def test_method_get_success_url(self):
        self.assertEqual(
            self.view.get_success_url(), reverse(settings.LOGIN_REDIRECT_URL))

    def test_method_get_success_url_with_next_kwarg(self):
        self.current_test_url = \
            self.current_test_url + '?next=' + self.next_url
        self.setUp()
        self.assertEqual(self.view.get_success_url(), self.next_url)

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'users/login.html')

    def test_request_get_method_authenticated_user(self):
        self.client.login(
            username=self.test_user, password=c.TEST_USER_PASSWORD)
        self.response = self.client.get(self.current_test_url)

        # redirects to settings.LOGIN_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGIN_REDIRECT_URL))

        # template contains c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE, self.html)

    def test_inactive_user_login(self):
        """
        What happens when an unconfirmed, or banned, user tries to log in?

            - Users with no last_login are treated as not-yet-activated,
              and will receive a message telling them to use the emailed link.
            - Users with a last_login are considered to be banned, and will
              behave normally, ie. return bad username/password ValidationError
        """
        unconfirmed_user = f.UserFactory(is_active=False)
        banned_user = f.UserFactory(is_active=False, last_login=timezone.now())

        # ensure that the unconfirmed user receives the correct message
        self.response = self.client.post(
            self.current_test_url, {
                'username': unconfirmed_user.username,
                'password': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})

        self.assertEquals(self.response.status_code, 200)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_IS_UNCONFIRMED_MESSAGE, self.html)

        # ensure that the banned user receives the correct message
        self.response = self.client.post(
            self.current_test_url, {
                'username': banned_user.username,
                'password': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})

        self.assertEquals(self.response.status_code, 200)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(
            "Please enter a correct username and password.", self.html)

        # try unbanning the above user to ensure that the ValidationError
        # above was not due to bad inputs
        banned_user.is_active = True
        banned_user.save()

        self.response = self.client.post(
            self.current_test_url, {
                'username': banned_user.username,
                'password': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'},
            follow=True)

        self.assertEquals(self.response.status_code, 200)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(c.USER_LOGIN_SUCCESS_MESSAGE, self.html)


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
        self.assertEqual(redirect_url, reverse('users:login'))
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'users/login.html')

    def test_get_method_authenticated_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, self.view.template_name)

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
        self.assertEqual(self.view.model, UserModel)

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message, c.USER_UPDATE_SUCCESS_MESSAGE)

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

        # template contains updated user information and success_message
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{updated_user_first_name}", self.html)
        self.assertIn(f"{updated_user_last_name}", self.html)
        self.assertIn(f"{self.test_user.email}", self.html)
        self.assertIn(self.view.success_message, self.html)


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

    def test_view_success_message(self):
        self.assertEqual(
            self.view.success_message, c.USER_LOGOUT_SUCCESS_MESSAGE)

    # request.GET
    def test_request_get_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGOUT_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGOUT_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)

    def test_request_get_method_authenticated_user(self):
        self.response = self.client.get(self.current_test_url)

        # redirect to settings.LOGOUT_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGOUT_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)

    def test_request_post_method_unauthenticated_user(self):
        self.client.logout()
        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGOUT_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGOUT_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # messages does not contain success_message
        self.assertNotIn(self.view.success_message, self.html)

    def test_request_post_method_authenticated_user(self):
        self.response = self.client.post(self.current_test_url)

        # redirect to settings.LOGOUT_REDIRECT_URL
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse(settings.LOGOUT_REDIRECT_URL))

        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))

        # template contains 1 message
        self.assertEqual(len(self.response.context['messages']), 1)

        # messages contains success_message
        self.assertIn(self.view.success_message, self.html)


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
        self.assertEqual(self.view.model, UserModel)

    def test_attribute_template_name(self):
        self.assertEqual(
            self.view.template_name, 'users/user_confirm_delete.html')

    def test_attribute_success_message(self):
        self.assertEqual(
            self.view.success_message, c.USER_DELETE_SUCCESS_MESSAGE)

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
        old_user_count = UserModel.objects.count()

        # delete user via POST
        self.response = self.client.post(self.current_test_url)

        # user is redirected to homepage
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('root'))

        # homepage loads successfully and contains success_message
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(self.view.success_message, self.html)

        # object no longer exists
        with self.assertRaises(UserModel.DoesNotExist):
            self.test_user.refresh_from_db()

        # user count decreased by 1
        new_user_count = UserModel.objects.count()
        self.assertEqual(old_user_count - 1, new_user_count)


class PasswordChangeViewTest(TestCase):

    def setUp(self):
        self.test_user = f.UserFactory()

        self.client.login(
            username=self.test_user.username, password=c.TEST_USER_PASSWORD)

        self.current_test_url = reverse('users:password_change')
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # view attributes
    def test_template_name(self):
        self.assertEqual(
            self.view.template_name, 'users/password_change_form.html')

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)


class PasswordResetViewTest(TestCase):

    def setUp(self):
        self.current_test_url = reverse('users:password_reset')
        self.response = self.client.get(self.current_test_url)
        self.view = self.response.context['view']

    # view attributes
    def test_form_class(self):
        self.assertEqual(
            self.view.form_class.__name__, 'UserPasswordResetForm')

    def test_template_name(self):
        self.assertEqual(
            self.view.template_name, 'users/password_reset_form.html')

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)
