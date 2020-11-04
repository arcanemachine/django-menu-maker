from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class NewUserCreationForm(UserCreationForm):

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
