from os.path import join as os_path_join
from pathlib import Path

SERVER_NAME = 'dev'
SERVER_LOCATION = '192.168.1.120:8000'
SERVER_EMAIL = 'admin@email.local'
DEBUG = True
ALLOWED_HOSTS = ['*']

FRONTEND_SERVER_URL = 'http://192.168.1.120:8081'

BASE_DIR = str(Path(__file__).resolve().parent)

STATIC_URL = '/static/'
STATICFILES_DIRS = [os_path_join(BASE_DIR, 'static')]
STATIC_ROOT = None
