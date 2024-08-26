import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Configure logging to debug level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file (for local development)
load_dotenv()

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

def get_google_credentials():
    if 'DYNO' in os.environ:
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        logger.debug("GOOGLE_CREDENTIALS_JSON from env: %s", google_credentials_json)
        return json.loads(google_credentials_json)
    else:
        google_credentials_path = os.path.join(BASE_DIR, 'credentials.json')
        logger.debug("Loading credentials from file: %s", google_credentials_path)
        if os.path.isfile(google_credentials_path):
            with open(google_credentials_path) as f:
                return json.load(f)
        else:
            logger.error("Local credentials file not found at: %s", google_credentials_path)
            raise FileNotFoundError(f"Local credentials file not found at: {google_credentials_path}")

# Load Google credentials
GOOGLE_CREDENTIALS = get_google_credentials()
GOOGLE_CLIENT_ID = GOOGLE_CREDENTIALS.get('client_id')  # Adjust based on your JSON structure
GOOGLE_CLIENT_SECRET = GOOGLE_CREDENTIALS.get('client_secret')  # Adjust based on your JSON structure

# Define other settings
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', '5b57-86-46-100-229.ngrok-free.app'] if DEBUG else os.getenv('ALLOWED_HOSTS', 'www.jwalshedev.ie').split(',')
GOOGLE_REDIRECT_URI = 'http://localhost:8000/oauth2callback/' if DEBUG else 'https://www.jwalshedev.ie/oauth2callback/'

SECRET_KEY = os.environ.get("SECRET_KEY")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Define GOOGLE_API_KEY
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", '')

# Token file path
TOKEN_FILE_PATH = os.path.join(BASE_DIR, 'token.json')

# Database configuration
HEROKU = 'DYNO' in os.environ
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    ) if HEROKU else {
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

# Static files (CSS, JavaScript, Images)
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

