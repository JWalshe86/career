import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve DEBUG setting
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Define ALLOWED_HOSTS

# Define ALLOWED_HOSTS
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'https://www.jwalshedev.ie').split(',')

DEFAULT_HOSTNAME = 'https://www.jwalshedev.ie'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# Google credentials
GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_REDIRECT_URI = 'https://www.jwalshedev.ie/oauth2callback/'

# Token file path
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

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

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
ROOT_URLCONF = 'career.urls'  # Update this if your project has a different module name

# WSGI configuration
WSGI_APPLICATION = 'career.wsgi.application'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

