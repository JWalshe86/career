import os
import json
import requests
import logging
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

def get_access_token():
    # Fetch the token from the environment or other secure storage
    google_credentials = get_google_credentials()
    return google_credentials.get('token')


def make_google_api_request(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()  # Attempt to parse JSON response
        return data
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    return None

def get_google_credentials():
    google_credentials_json = os.getenv('GMAIL_TOKEN_JSON')
    logger.debug(f"GMAIL_TOKEN_JSON retrieved: {google_credentials_json}")
    if not google_credentials_json:
        logger.error("GMAIL_TOKEN_JSON environment variable not found.")
        raise EnvironmentError("GMAIL_TOKEN_JSON environment variable not found.")
    
    try:
        credentials = json.loads(google_credentials_json)
        logger.debug(f"GOOGLE_CREDENTIALS loaded: {credentials}")
        return credentials
    except json.JSONDecodeError as e:
        logger.error("Error decoding GMAIL_TOKEN_JSON: %s", e)
        raise ValueError("Error decoding GMAIL_TOKEN_JSON") from e

def refresh_google_token():
    credentials = get_google_credentials()
    
    payload = {
        'client_id': credentials['client_id'],
        'client_secret': credentials['client_secret'],
        'refresh_token': credentials['refresh_token'],
        'grant_type': 'refresh_token',
    }

    response = requests.post(credentials['token_uri'], data=payload)
    
    if response.status_code == 200:
        new_token_info = response.json()
        new_token_info['refresh_token'] = credentials['refresh_token']  # Keep the original refresh token
        return new_token_info
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

# Example usage
try:
    new_token_info = refresh_google_token()
    token = new_token_info['access_token']  # Use this token
    data = make_google_api_request('https://www.googleapis.com/some_endpoint', token)
    if data:
        logger.info(f"API response data: {data}")
    else:
        logger.error("Failed to get data from API.")
except Exception as e:
    logger.error(f"Failed to refresh token: {e}")

def env_view(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')  # Replace with your actual secret key handling




# Check if the app is running on Heroku
HEROKU = 'DYNO' in os.environ

if HEROKU:  # Heroku environment
    logger.debug(f"GOOGLE_CREDENTIALS_JSON from environment: {os.getenv('GMAIL_TOKEN_JSON')}")
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
GOOGLE_CREDENTIALS = get_google_credentials()
GOOGLE_CLIENT_ID = GOOGLE_CREDENTIALS.get('client_id')
GOOGLE_CLIENT_SECRET = GOOGLE_CREDENTIALS.get('client_secret')
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
logger.debug(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")

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

# Function to refresh Google token
def refresh_google_token():
    credentials = get_google_credentials()
    
    payload = {
        'client_id': credentials['client_id'],
        'client_secret': credentials['client_secret'],
        'refresh_token': credentials['refresh_token'],
        'grant_type': 'refresh_token',
    }

    response = requests.post(credentials['token_uri'], data=payload)
    
    if response.status_code == 200:
        new_token_info = response.json()
        new_token_info['refresh_token'] = credentials['refresh_token']  # Keep the original refresh token
        return new_token_info
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

# Example usage of refreshing the token
# Ensure this code is executed in an appropriate context (e.g., management command or scheduled task)
try:
    new_token_info = refresh_google_token()
    print(f"New token: {new_token_info['access_token']}, expires in: {new_token_info['expires_in']} seconds")
except Exception as e:
    logger.error(f"Failed to refresh token: {e}")

def env_view(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

# Ensure that the secret key and other settings are properly loaded
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')  # Replace with your actual secret key handling

