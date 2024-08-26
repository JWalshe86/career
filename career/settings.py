import os
import json
import dj_database_url
from django.http import HttpResponse
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def env_view(request):
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {os.getenv('GOOGLE_CREDENTIALS_JSON')}")

# Load environment variables
load_dotenv()

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY=os.getenv('SECRET_KEY')

def get_google_credentials():
    # Check if the environment variable is set
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not google_credentials_json:
        logger.error("GOOGLE_CREDENTIALS_JSON environment variable not found.")
        raise EnvironmentError("GOOGLE_CREDENTIALS_JSON environment variable not found.")

    # Try to parse the JSON
    try:
        credentials = json.loads(google_credentials_json)
        logger.debug("Successfully parsed GOOGLE_CREDENTIALS_JSON.")
        return credentials
    except json.JSONDecodeError as e:
        logger.error("Error decoding GOOGLE_CREDENTIALS_JSON: %s", e)
        raise
# Load Google credentials
GOOGLE_CREDENTIALS = get_google_credentials()

# Extract values
GOOGLE_CLIENT_ID = GOOGLE_CREDENTIALS.get('web', {}).get('client_id')
GOOGLE_CLIENT_SECRET = GOOGLE_CREDENTIALS.get('web', {}).get('client_secret')

# Additional settings
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(',')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/oauth2callback')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

TOKEN_FILE_PATH = os.path.join(BASE_DIR, 'token.json')

# Database configuration
HEROKU = 'DYNO' in os.environ
if HEROKU:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DB_NAME', 'test_db'),
            'USER': os.environ.get('MYSQL_DB_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_DB_PASSWORD', 'Sunshine7!'),
            'HOST': os.environ.get('MYSQL_DB_HOST', 'localhost'),
            'PORT': os.environ.get('MYSQL_DB_PORT', '3306'),
        }
    }
# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://www.jwalshedev.ie',
    'https://johnsite.herokuapp.com',
    'https://5b57-86-46-100-229.ngrok-free.app',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# URLs configuration
ROOT_URLCONF = 'career.urls'

# WSGI configuration
WSGI_APPLICATION = 'career.wsgi.application'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
    'tasks',
    'jobs',
    'map',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
