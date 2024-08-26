import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from django.http import HttpResponse
import dj_database_url

# Load environment variables from .env file (for local development)
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve DEBUG setting
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Define ALLOWED_HOSTS based on environment
if DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', '5b57-86-46-100-229.ngrok-free.app']
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'www.jwalshedev.ie').split(',')

# Define Google Redirect URI based on environment
GOOGLE_REDIRECT_URI = 'http://localhost:8000/oauth2callback/' if DEBUG else 'https://www.jwalshedev.ie/oauth2callback/'

# Security settings
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Google credentials
HEROKU = 'DYNO' in os.environ
if HEROKU:  # Heroku environment
    GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
    logger.debug(f"GOOGLE_CREDENTIALS_JSON from environment: {GOOGLE_CREDENTIALS_JSON}")
    if not GOOGLE_CREDENTIALS_JSON:
        raise EnvironmentError("GOOGLE_CREDENTIALS_JSON environment variable not found or is empty.")
    try:
        GOOGLE_CREDENTIALS = json.loads(GOOGLE_CREDENTIALS_JSON)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON") from e
else:  # Local environment
    GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
    if not os.path.isfile(GOOGLE_CREDENTIALS_PATH):
        raise FileNotFoundError(f"File not found: {GOOGLE_CREDENTIALS_PATH}")
    try:
        with open(GOOGLE_CREDENTIALS_PATH) as f:
            GOOGLE_CREDENTIALS = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON from file") from e

# Extract values
GOOGLE_CLIENT_ID = GOOGLE_CREDENTIALS.get('client_id')
GOOGLE_CLIENT_SECRET = GOOGLE_CREDENTIALS.get('client_secret')

logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
logger.debug(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Token file path
TOKEN_FILE_PATH = os.path.join(BASE_DIR, 'token.json')

# Database configuration
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


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to load Google credentials
# Example view to display Google credentials JSON for debugging
def load_google_credentials():
    if 'DYNO' in os.environ:  # Heroku environment
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not google_credentials_json:
            logger.error("GOOGLE_CREDENTIALS_JSON environment variable not found.")
            raise EnvironmentError("GOOGLE_CREDENTIALS_JSON environment variable not found.")
        try:
            credentials = json.loads(google_credentials_json)
            logger.debug("Successfully parsed GOOGLE_CREDENTIALS_JSON from environment.")
            return credentials
        except json.JSONDecodeError as e:
            logger.error("Error decoding GOOGLE_CREDENTIALS_JSON: %s", e)
            raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON") from e
    else:  # Local environment
        google_credentials_path = os.path.join(BASE_DIR, 'credentials.json')
        if not os.path.isfile(google_credentials_path):
            logger.error("File not found: %s", google_credentials_path)
            raise FileNotFoundError(f"File not found: {google_credentials_path}")
        try:
            with open(google_credentials_path) as f:
                credentials = json.load(f)
                logger.debug("Successfully loaded GOOGLE_CREDENTIALS_JSON from file.")
                return credentials
        except json.JSONDecodeError as e:
            logger.error("Error decoding GOOGLE_CREDENTIALS_JSON from file: %s", e)
            raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON from file") from e

# Load Google credentials
GOOGLE_CREDENTIALS = load_google_credentials()
print('google credentials', GOOGLE_CREDENTIALS)
def env_view(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

# Ensure that the secret key and other settings are properly loaded
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')  # Replace with your actual secret key handling















