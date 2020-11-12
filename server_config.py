from os.path import join as os_path_join
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent)

SERVER_NAME = 'dev'
DEBUG = True

STATICFILES_DIRS = [os_path_join(BASE_DIR, 'static')]
STATIC_ROOT = None
