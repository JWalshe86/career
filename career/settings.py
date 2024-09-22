import os
import json
import logging
from pathlib import Path
from decouple import config, Csv
from dotenv import load_dotenv
import dj_database_url


# Load Gmail token JSON from environment variable
GMAIL_TOKEN_JSON = os.getenv('GMAIL_TOKEN_JSON')
if GMAIL_TOKEN_JSON:
    GMAIL_TOKEN_JSON = json.loads(GMAIL_TOKEN_JSON)

DEFAULT_HOSTNAME = 'www.jwalshedev.ie'  # Adjust as needed


# Load environment variables from .env file (for local development)
load_dotenv()
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://www.jwalshedev.ie,https://johnsite.herokuapp.com,https://4f81-84-203-41-130.ngrok-free.app', cast=Csv())
# Determine if running on Heroku
HEROKU = 'DYNO' in os.environ

DEBUG = config('DEBUG', default=False, cast=bool)
ROOT_URLCONF = 'career.urls'


if DEBUG:
    GOOGLE_REDIRECT_URI = 'http://localhost:9000/oauth/callback/'
else:
    GOOGLE_REDIRECT_URI = 'https://www.jwalshedev.ie/oauth/callback/'

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URIS = [
        'https://www.jwalshedev.ie/oauth/callback/',
                ]
GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='')
print(f"GOOGLE_CLIENT_ID in setting.py: {GOOGLE_CLIENT_ID}")
print(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")
print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}")

SCOPES = json.loads(os.getenv('SCOPES', '["https://www.googleapis.com/auth/gmail.readonly"]'))
TOKEN_JSON_PATH = os.getenv('TOKEN_JSON_PATH', 'token.json')
google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
if google_credentials_json:
    try:
        GOOGLE_CREDENTIALS = json.loads(google_credentials_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_CREDENTIALS_JSON: {e}")
else:
    raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set.")
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve settings
SECRET_KEY = config('SECRET_KEY', default='default-secret-key')
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '4f81-84-203-41-130.ngrok-free.app',  # Add ngrok domain here
    'www.jwalshedev.ie',
    # other domains
]

DATABASE_URL = config('DATABASE_URL', default='')

# Database configuration
if HEROKU:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',  # Change to PostgreSQL
            'NAME': config('POSTGRES_DB_NAME', default='career_db'),  # Update with your DB name
            'USER': config('POSTGRES_DB_USER', default='johnwalshe'),  # Update with your user
            'PASSWORD': config('POSTGRES_DB_PASSWORD', default='Sunshine7!'),  # Keep your password
            'HOST': config('POSTGRES_DB_HOST', default='localhost'),  # Keep as localhost
            'PORT': config('POSTGRES_DB_PORT', default='5432'),  # Default PostgreSQL port
        }
    }

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']


import logging

# settings.py

import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',  # Use verbose formatter for more detail
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'emails.utils': {  # Your module name for specific logging
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'emails',
    'oauth', 
    'dashboard',
    'decouple',
    'tasks',
    'jobs',
    'errors',
    'map',
    'users',
	'debug_toolbar',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'jobs.context_processors.unread_email_count',
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

# WSGI configuration
WSGI_APPLICATION = 'career.wsgi.application'


INTERNAL_IPS = [
    # ...
    '127.0.0.1',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}
