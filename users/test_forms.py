from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from users.forms import NewUserCreationForm


class NewUserCreationFormTest(SimpleTestCase):

    def setUp(self):
        self.form = NewUserCreationForm
        self.form_instance = NewUserCreationForm()

    def test_meta_model_name(self):
        self.assertEqual(self.form.Meta.model, get_user_model())

    def test_meta_fields(self):
        self.assertEqual(self.form.Meta.fields, ('username', 'email'))

    def test_init_email_required(self):
        self.assertEqual(self.form_instance.fields['email'].required, True)
