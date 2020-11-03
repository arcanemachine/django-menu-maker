from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

User = get_user_model()


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy(settings.LOGIN_URL)
    success_message = "Account successfully registered"

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'

    def get_object(self):
        return self.request.user

class UserLogoutView(LogoutView):
    success_message = "You have successfully logged out."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, self.success_message)
        return super().dispatch(request, *args, **kwargs)
