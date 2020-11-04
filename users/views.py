from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import UpdateView

from .forms import NewUserCreationForm


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = NewUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy(settings.LOGIN_URL)
    success_message = "Your account has been successfully registered."


class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'

    def get_object(self):
        return self.request.user


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = 'users/user_update.html'
    fields = ('first_name', 'last_name', 'email')
    success_message = "You have updated your personal information."
    success_url = reverse_lazy('users:user_detail')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        return {'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email}


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'users/user_confirm_delete.html'
    success_message = "Your account has been deleted."
    success_url = reverse_lazy('root')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class UserLogoutView(LogoutView):
    success_message = "You have successfully logged out."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, self.success_message)
        return super().dispatch(request, *args, **kwargs)
