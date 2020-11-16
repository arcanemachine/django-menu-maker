"""
Generated by 'django-admin startproject' using Django 3.1.2.
"""

import os
import sys

from pathlib import Path

import secret_key
import server_config

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = server_config.DEBUG
SECRET_KEY = secret_key.SECRET_KEY
ALLOWED_HOSTS = ['*']


# application

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local
    'api.apps.ApiConfig',
    'menus.apps.MenusConfig',
    'restaurants.apps.RestaurantsConfig',
    'users.apps.UsersConfig',
    # third-party
    'allauth',
    'allauth.account',
    'captcha',
    'crispy_forms',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'menus_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(os.path.join(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'menus_project.context_processors.project_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'menus_project.wsgi.application'

# database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# allauth
SITE_ID = 1

# authentication
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:user_detail'
LOGOUT_REDIRECT_URL = 'root'

# captcha
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_NOISE_FUNCTIONS = []
CAPTCHA_LETTER_ROTATION = (-20, 25)

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    CAPTCHA_TEST_MODE = True

# email
EMAIL_CONFIRMATION_REQUIRED = False
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SERVER_EMAIL = server_config.SERVER_EMAIL

# forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# passwords
validation_string = 'django.contrib.auth.password_validation.'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': validation_string + 'UserAttributeSimilarityValidator'},
    {'NAME': validation_string + 'MinimumLengthValidator'},
    {'NAME': validation_string + 'CommonPasswordValidator'},
    {'NAME': validation_string + 'NumericPasswordValidator'}]

# static files
STATIC_URL = '/static/'
STATICFILES_DIRS = server_config.STATICFILES_DIRS
STATIC_ROOT = server_config.STATIC_ROOT

# rest framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
