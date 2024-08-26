import os
import json
import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta
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
ALLOWED_HOSTS = ['127.0.0.1', '5b57-86-46-100-229.ngrok-free.app'] if DEBUG else os.getenv('ALLOWED_HOSTS', 'www.jwalshedev.ie').split(',')

# Define Google Redirect URI based on environment
GOOGLE_REDIRECT_URI = 'http://localhost:8000/oauth2callback/' if DEBUG else 'https://www.jwalshedev.ie/jobs/oauth2callback/'

# Security settings
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Save token to environment (or you can store it securely in a file or database)
def save_token_to_file(token_info):
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(token_info, f)


def get_access_token():
    if os.path.isfile(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH) as f:
            token_info = json.load(f)
        if 'access_token' in token_info and 'expiry' in token_info:
            expiry = datetime.fromisoformat(token_info['expiry'].replace('Z', '+00:00'))
            if datetime.utcnow() < expiry:
                return token_info['access_token']
    
    # Retrieve or refresh access token
    token_info = refresh_google_token()
    save_token_to_file(token_info)
    return token_info['access_token']

# Retrieve Google credentials from environment
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

# Refresh Google token when it expires
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
        
        # Extract expires_in and calculate the new expiry
        expires_in = new_token_info.get('expires_in', 3600)
        new_expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        new_token_info['expiry'] = new_expiry_time.isoformat() + 'Z'
        
        return new_token_info
    else:
        logger.error(f"Failed to refresh token: {response.text}")
        raise Exception(f"Failed to refresh token: {response.text}")

# Get information about the current token
def get_token_info(token):
    response = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}')
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to get token info: {response.text}")
        return None

# Make an API request to Google services using the access token
def make_google_api_request(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    return None

# Example usage
try:
    token = get_access_token()
    url = 'https://www.googleapis.com/gmail/v1/users/me/messages'
    data = make_google_api_request(url, token)
    if data:
        logger.info(f"API response data: {data}")
    else:
        logger.error("Failed to get data from API.")
except Exception as e:
    logger.error(f"An error occurred: {e}")

# Django view to display environment variable
def env_view(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

# Other Django and environment configurations
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

