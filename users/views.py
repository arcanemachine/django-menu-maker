from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import UpdateView

from menus_project import constants as c
from . import forms


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = forms.NewUserCreationForm
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
        elif self.request.user.is_authenticated:
            return reverse(settings.LOGIN_REDIRECT_URL)
        elif settings.EMAIL_CONFIRMATION_REQUIRED:
            return reverse('root')
        else:
            return reverse(settings.LOGIN_URL)


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = forms.UserAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_message = c.USER_LOGIN_SUCCESS_MESSAGE

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(request, c.USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)


class UserActivationView(UserLoginView):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.user_pk = int(urlsafe_base64_decode(self.kwargs['uidb64']))
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        messages.info(request, c.USER_ACTIVATION_VIEW_MESSAGE)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.user_pk
        kwargs['token'] = self.kwargs['token']
        return kwargs

    def form_valid(self, form):
        if form.token_is_valid:
            auth_login(self.request, form.temp_user)
            messages.success(self.request, c.USER_ACTIVATION_SUCCESS_MESSAGE)
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.success(self.request, c.USER_LOGIN_SUCCESS_MESSAGE)
            return super().form_valid(form)


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
