from os.path import join as os_path_join
from pathlib import Path

SERVER_NAME = 'prod'
SERVER_LOCATION = 'https://django-menu-maker.nicholasmoen.com'
SERVER_EMAIL = 'no-reply@nicholasmoen.com'
DEBUG = False

FRONTEND_SERVER_URL = SERVER_LOCATION

BASE_DIR = str(Path(__file__).resolve().parent)

STATIC_URL = '/staticfiles/'
STATICFILES_DIRS = [os_path_join(BASE_DIR, 'static')]
STATIC_ROOT = os_path_join(BASE_DIR, 'staticfiles')
