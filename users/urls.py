"""
django.contrib.auth views:

    register/  'register'                          users.RegisterView
    login/  'login'                                LoginView
    logout/  'logout'                              LogoutView
    password_change/  'password_change'            PasswordChangeForm
    password_change/done/  'password_change_done'  PasswordChangeDoneView
    password_reset/  'password_reset'              PasswordResetView
    password_reset/done/  'password_reset_done'    PasswordResetDoneView
    reset/<uidb64>/<token>/ password_reset_confirm PasswordResetConfirmView
    reset/done/  'password_reset_complete'         PasswordResetCompleteView
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import UserPasswordResetForm

app_name = 'users'

urlpatterns = [
    # users.views
    path('register/',
         views.RegisterView.as_view(),
         name='register'),
    path('login/',
         views.UserLoginView.as_view(),
         name='login'),
    path('login/<uidb64>/<token>/',
         views.UserActivationView.as_view(),
         name='user_activation'),
    path('me/',
         views.UserDetailView.as_view(),
         name='user_detail'),
    path('me/edit/',
         views.UserUpdateView.as_view(),
         name='user_update'),
    path('logout/',
         views.UserLogoutView.as_view(),
         name='logout'),
    path('me/delete-account/',
         views.UserDeleteView.as_view(),
         name='user_delete'),
    # django.contrib.auth.views
    path('me/change-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change_form.html'),
         name='password_change'),
    path('forgot-password/',
         auth_views.PasswordResetView.as_view(
             form_class=UserPasswordResetForm,
             template_name='users/password_reset_form.html'),
         name='password_reset'),
    ]
