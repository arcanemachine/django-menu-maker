from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import SimpleTestCase, TestCase
from django.utils.http import urlsafe_base64_decode
from html import unescape

from menus_project import constants as c
from menus_project import factories as f
from .forms import (
    NewUserCreationForm, UserAuthenticationForm, UserPasswordResetForm)


class NewUserCreationFormTest(TestCase):

    def setUp(self):
        self.form = NewUserCreationForm
        self.form_instance = NewUserCreationForm()

    def test_field_captcha_exists(self):
        self.assertTrue('captcha' in self.form_instance.fields)

    def test_field_captcha_field_type(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].__class__.__name__,
            'CaptchaField')

    def test_field_captcha_help_text(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].help_text,
            c.FORMS_CAPTCHA_FIELD_HELP_TEXT)

    def test_meta_model_name(self):
        self.assertEqual(self.form.Meta.model, get_user_model())

    def test_meta_fields(self):
        self.assertEqual(self.form.Meta.fields, ('username', 'email'))

    def test_init_email_required(self):
        self.assertEqual(self.form_instance.fields['email'].required, True)

    def test_validation_success(self):
        self.form_instance = \
            NewUserCreationForm(data={
                'username': c.TEST_USER_USERNAME,
                'email': c.TEST_USER_EMAIL,
                'password1': c.TEST_USER_PASSWORD,
                'password2': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})
        self.assertTrue(self.form_instance.is_valid())

    def test_validation_fail_duplicate_email(self):
        self.test_user = get_user_model().objects.create(
            username=c.TEST_USER_USERNAME,
            email=c.TEST_USER_EMAIL)
        self.form_instance = \
            NewUserCreationForm(data={
                'username': f'new_{self.test_user.username}',
                'email': self.test_user.email,
                'password1': c.TEST_USER_PASSWORD,
                'password2': c.TEST_USER_PASSWORD,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})
        self.assertFalse(self.form_instance.is_valid())
        self.assertEqual(
            self.form_instance.errors,
            {'email': ['This email address is already in use.']})

    # methods
    def test_method_send_new_user_email(self):
        """
        This method is an abominable hack that should be moved out of
        the form and into its own functions. However, it is tightly
        coupled to Django's native password reset function, and may
        benefit from any improvements that are made to it.
        """
        test_user = f.UserFactory()
        other_user = f.UserFactory()

        with self.settings(EMAIL_CONFIRMATION_REQUIRED=True):
            # uid matches self.test_user.pk
            uid = \
                self.form_instance.send_new_user_email(test_user, get_uid=True)
            self.assertEqual(int(urlsafe_base64_decode(uid)), test_user.pk)

            # token is valid
            test_user_token = self.form_instance.send_new_user_email(
                test_user, get_token=True)
            self.assertTrue(default_token_generator.check_token(
                test_user, test_user_token))

            # check_token - token returned by the method always returns True
            self.form_instance.send_new_user_email(test_user, check_token=True)

            # check_token - a manually-entered token
            # for the same user always returns True
            self.assertTrue(self.form_instance.send_new_user_email(
                test_user, check_token=True, token=test_user_token))

            # check_token - a manually-entered token for
            # a different user always returns False
            other_user_token = self.form_instance.send_new_user_email(
                other_user, get_token=True)
            self.assertFalse(self.form_instance.send_new_user_email(
                test_user, check_token=True, token=other_user_token))

            # url is valid
            user_activation_url = \
                self.form_instance.send_new_user_email(test_user, get_url=True)
            self.response = self.client.get(user_activation_url)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_VIEW_MESSAGE, self.html)

            # path is valid
            user_activation_url = self.form_instance.send_new_user_email(
                test_user, get_path=True)
            self.response = self.client.get(user_activation_url)
            self.assertEqual(self.response.status_code, 200)
            self.html = unescape(self.response.content.decode('utf-8'))
            self.assertIn(c.USER_ACTIVATION_VIEW_MESSAGE, self.html)

            # confirmation email sent and contains expected text
            self.form_instance.send_new_user_email(test_user)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Confirm your account", mail.outbox[0].subject)
            self.assertIn("confirm your account", mail.outbox[0].body)

    def test_welcome_email(self):
        test_user = f.UserFactory()

        # url is valid
        with self.settings(EMAIL_CONFIRMATION_REQUIRED=False):
            user_activation_url = \
                self.form_instance.send_new_user_email(test_user, get_url=True)
            self.response = self.client.get(user_activation_url)
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, 'users/login.html')

            # confirmation email sent and contains expected text
            self.form_instance.send_new_user_email(test_user)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(
                f"Welcome to {c.PROJECT_NAME}!", mail.outbox[0].subject)
            self.assertIn(
                "You can login to your account", mail.outbox[0].body)


class UserAuthenticationFormTest(SimpleTestCase):

    def setUp(self):
        self.form = UserAuthenticationForm
        self.form_instance = UserAuthenticationForm()

    def test_field_captcha_exists(self):
        self.assertTrue('captcha' in self.form_instance.fields)

    def test_field_captcha_field_type(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].__class__.__name__,
            'CaptchaField')

    def test_field_captcha_help_text(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].help_text,
            c.FORMS_CAPTCHA_FIELD_HELP_TEXT)


class UserPasswordResetFormTest(SimpleTestCase):

    def setUp(self):
        self.form = UserPasswordResetForm
        self.form_instance = UserPasswordResetForm()

    def test_field_captcha_exists(self):
        self.assertTrue('captcha' in self.form_instance.fields)

    def test_field_captcha_field_type(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].__class__.__name__,
            'CaptchaField')

    def test_field_captcha_help_text(self):
        self.assertEqual(
            self.form_instance.fields['captcha'].help_text,
            c.FORMS_CAPTCHA_FIELD_HELP_TEXT)
