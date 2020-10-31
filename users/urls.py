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
from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'),
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'),
    ]
