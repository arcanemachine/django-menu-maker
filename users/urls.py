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

app_name = 'users'

urlpatterns = [
    # users.views
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'),
    path(
        'me/',
        views.UserDetailView.as_view(),
        name='user_detail'),
    path(
        'me/edit/',
        views.UserUpdateView.as_view(),
        name='user_update'),
    path(
        'me/delete-account/',
        views.UserDeleteView.as_view(),
        name='user_delete'),
    path(
        'logout/',
        views.UserLogoutView.as_view(),
        name='logout'),
    # django.contrib.auth.views
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login'),
    path(
        'me/change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'),
        name='password_change'),
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
        name='password_reset'),
    ]
