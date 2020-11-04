from django.contrib.auth import get_user_model
from django.test import TestCase

from .forms import NewUserCreationForm
from menus_project import constants

test_user_username = constants.test_user_username
test_user_email = constants.test_user_email
test_user_password = constants.test_user_password

class NewUserCreationFormTest(TestCase):

    def setUp(self):
        self.form = NewUserCreationForm
        self.form_instance = NewUserCreationForm()

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
                })
        self.assertTrue(self.form_instance.is_valid())

    def test_validation_fail_duplicate_email(self):
        self.test_user = get_user_model().objects.create(
            username=test_user_username,
            email=test_user_email)
        self.form_instance = \
            NewUserCreationForm(data={'email': self.test_user.email})
        self.assertFalse(self.form_instance.is_valid())
