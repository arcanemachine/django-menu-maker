from captcha.fields import CaptchaField
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, UserCreationForm)
from django.core.exceptions import ValidationError

from menus_project import constants as c


class NewUserCreationForm(UserCreationForm):

    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)

    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        # do not allow duplicate email addresses
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email


class UserAuthenticationForm(AuthenticationForm):

    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)


class UserPasswordResetForm(PasswordResetForm):

    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)
