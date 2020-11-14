from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import UpdateView

from menus_project import constants as c
from .forms import NewUserCreationForm, UserAuthenticationForm


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = NewUserCreationForm
    template_name = 'users/register.html'
    success_message = c.USER_REGISTER_SUCCESS_MESSAGE

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(
                request, c.USER_REGISTER_ALREADY_AUTHENTICATED_MESSAGE)
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.GET.get('next', None):
            return self.request.GET['next']
        if self.request.user.is_authenticated:
            return reverse(settings.LOGIN_REDIRECT_URL)
        return reverse(settings.LOGIN_URL)


class LoginView(SuccessMessageMixin, LoginView):
    form_class = UserAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_message = c.USER_LOGIN_SUCCESS_MESSAGE

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(request, c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.GET.get('next', None):
            return self.request.GET['next']
        return reverse(settings.LOGIN_REDIRECT_URL)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'

    def get_object(self):
        return self.request.user


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    template_name = 'users/user_update.html'
    fields = ('first_name', 'last_name', 'email')
    success_message = c.USER_UPDATE_SUCCESS_MESSAGE
    success_url = reverse_lazy('users:user_detail')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        return {'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email}


class UserLogoutView(LogoutView):
    success_message = c.USER_LOGOUT_SUCCESS_MESSAGE

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, self.success_message)
        return super().dispatch(request, *args, **kwargs)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'users/user_confirm_delete.html'
    success_message = c.USER_DELETE_SUCCESS_MESSAGE
    success_url = reverse_lazy('root')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return self.request.user
