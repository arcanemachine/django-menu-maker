from django.contrib.auth import get_user_model
from django.test import TestCase

from .forms import NewUserCreationForm
from menus_project import constants

test_user_username = constants.TEST_USER_USERNAME
test_user_email = constants.TEST_USER_EMAIL
test_user_password = constants.TEST_USER_PASSWORD


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
            "Please enter the letters you see in the image above.")

    def test_meta_model_name(self):
        self.assertEqual(self.form.Meta.model, get_user_model())

    def test_meta_fields(self):
        self.assertEqual(self.form.Meta.fields, ('username', 'email'))

    def test_init_email_required(self):
        self.assertEqual(self.form_instance.fields['email'].required, True)

    def test_validation_success(self):
        self.form_instance = \
            NewUserCreationForm(data={
                'username': test_user_username,
                'email': test_user_email,
                'password1': test_user_password,
                'password2': test_user_password,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})
        self.assertTrue(self.form_instance.is_valid())

    def test_validation_fail_duplicate_email(self):
        self.test_user = get_user_model().objects.create(
            username=test_user_username,
            email=test_user_email)
        self.form_instance = \
            NewUserCreationForm(data={
                'username': f'new_{self.test_user.username}',
                'email': self.test_user.email,
                'password1': test_user_password,
                'password2': test_user_password,
                'captcha_0': 'test',
                'captcha_1': 'PASSED'})
        self.assertFalse(self.form_instance.is_valid())
        self.assertEqual(
            self.form_instance.errors,
            {'email': ['This email address is already in use.']})
