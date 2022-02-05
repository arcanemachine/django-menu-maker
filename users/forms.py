from captcha.fields import CaptchaField
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, UserCreationForm)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

from server_config import SERVER_LOCATION
from menus_project import constants as c

UserModel = get_user_model()


class NewUserCreationForm(PasswordResetForm, UserCreationForm):
    """Register new users and send them a welcome email."""
    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)

    class Meta:
        model = UserModel
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        self.next_url = kwargs.pop('next_url', None)
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    # do not allow duplicate email addresses
    def clean_email(self):
        email = self.cleaned_data['email']
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def save(self, *args, **kwargs):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user = self.send_new_user_email(
            user=user, next_url=self.next_url, update_user=True)
        return user

    def send_new_user_email(
            self, user, get_url=False, next_url=None, get_next_url=False,
            get_path=False, get_uid=False, get_token=False, check_token=False,
            token=None, update_user=False, use_https=False,
            extra_email_context=None, *args, **kwargs):
        if settings.EMAIL_CONFIRMATION_REQUIRED:
            if update_user:
                user.is_active = False
                user.save()
            subject_template_name = 'users/user_confirmation_subject.txt'
            email_template_name = 'users/user_confirmation_email.html'
        else:
            if update_user:
                user.save()
            subject_template_name = 'users/user_welcome_subject.txt'
            email_template_name = 'users/user_welcome_email.html'
        token_generator = default_token_generator
        from_email = settings.SERVER_EMAIL
        user_email = user.email
        html_email_template_name = None
        extra_email_context = {'PROJECT_NAME': c.PROJECT_NAME}
        if next_url is None:
            next_url = ''
        else:
            next_url = f'?next={next_url}'
        if token is None:
            token = token_generator.make_token(user)
        context = {'token': token,
                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                   'email': user.email,
                   'next_url': next_url,
                   'domain': SERVER_LOCATION,
                   'site_name': SERVER_LOCATION,
                   'username': user.username,
                   'protocol': 'https' if use_https else 'http',
                   **(extra_email_context or {})}
        if get_uid:
            return context['uid']
        if get_token:
            return context['token']
        if check_token:
            return token_generator.check_token(user, token)
        if get_next_url:
            return next_url
        if get_path or get_url:
            protocol = context['protocol']
            domain = context['domain']
            if settings.EMAIL_CONFIRMATION_REQUIRED:
                base_url = reverse('users:user_activation', kwargs={
                    'uidb64': context['uid'],
                    'token': context['token']})
            else:
                base_url = reverse(settings.LOGIN_URL)
            if get_path:
                return f'{base_url}{next_url}'
            if get_url:
                return f'{domain}{base_url}{next_url}'
        self.send_mail(
            subject_template_name, email_template_name, context, from_email,
            user_email, html_email_template_name=html_email_template_name)
        return user


class UserAuthenticationForm(AuthenticationForm):
    """Perform login, validate unconfirmed user accounts."""
    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)

    def __init__(self, *args, **kwargs):
        self.temp_user = None
        self.user_pk = kwargs.pop('user_pk', None)
        self.token = kwargs.pop('token', None)
        self.token_is_valid = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)
            # only unconfirmed and banned users will make it past this point
            if self.user_cache is None:

                try:
                    self.temp_user = UserModel.objects.get(username=username)
                except UserModel.DoesNotExist:
                    self.temp_user = None

                # only unconfirmed users will make it past this point
                if self.temp_user is not None \
                        and self.temp_user.check_password(password) \
                        and self.temp_user.last_login is None:

                    # do not process user activation if the form has errors
                    if not self.errors:

                        # if account is unconfirmed, confirm the account
                        if self.token is not None \
                                and not self.temp_user.is_active:
                            try:
                                self.token_is_valid = \
                                    default_token_generator.check_token(
                                        self.temp_user, self.token)
                            except ValueError:
                                raise ValidationError(
                                    c.USER_ACTIVATION_INVALID_URL_MESSAGE)

                            if self.token_is_valid \
                                    and self.user_pk == self.temp_user.pk:
                                self.temp_user.is_active = True
                                self.temp_user.save()
                            else:
                                raise ValidationError(
                                    "This validation URL is invalid.")
                        # notify unconfirmed user to check their email inbox
                        elif not self.temp_user.is_active:
                            raise ValidationError(
                                c.USER_IS_UNCONFIRMED_MESSAGE)
                # only banned users will make it past this point
                else:
                    raise self.get_invalid_login_error()
        return self.cleaned_data


class UserPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(
        help_text=c.FORMS_CAPTCHA_FIELD_HELP_TEXT)
