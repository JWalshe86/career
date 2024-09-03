import os
import json
import logging
from pathlib import Path
from decouple import config, Csv
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file (for local development)
load_dotenv()

# Determine if running on Heroku
HEROKU = 'DYNO' in os.environ


DEBUG = config('DEBUG', default=False, cast=bool)
ROOT_URLCONF = 'career.urls'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
SCOPES = json.loads(os.getenv('SCOPES', '["https://www.googleapis.com/auth/gmail.readonly"]'))

# Check environment
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

# Further logic depending on the presence of credentials
if GOOGLE_CREDENTIALS_PATH:
    # Load credentials only if path is provided
    try:
        credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
        service = build('your_service_name', 'v1', credentials=credentials)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        service = None
else:
    # Handle cases where credentials are not provided
    print("No credentials provided; some features may be unavailable.")
    service = None


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve settings
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,5b57-86-46-100-229.ngrok-free.app,johnsite-d251709cf12b.herokuapp.com,www.jwalshedev.ie', cast=Csv())
SECRET_KEY = config('SECRET_KEY', default='default-secret-key')
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
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('MYSQL_DB_NAME', default='test_db'),
            'USER': config('MYSQL_DB_USER', default='root'),
            'PASSWORD': config('MYSQL_DB_PASSWORD', default='Sunshine7!'),
            'HOST': config('MYSQL_DB_HOST', default='localhost'),
            'PORT': config('MYSQL_DB_PORT', default='3306'),
        }
    }

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.utils': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'career.middleware.custom_error_middleware.CustomErrorMiddleware',  # Custom middleware
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
    'oauth',  # Your new app
    'dashboard',
    'decouple',
    'tasks',
    'jobs',
    'map',
    'users',
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

