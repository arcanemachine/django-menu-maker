from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy(settings.LOGIN_URL)
    template_name = 'registration/register.html'
