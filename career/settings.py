import os
import json
import requests
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decouple import config, Csv
from dotenv import load_dotenv
from django.http import HttpResponse
import dj_database_url

# Load environment variables from .env file (for local development)
load_dotenv()

# In settings.py
import os
print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve DEBUG setting using python-decouple
DEBUG = config('DEBUG', default=False, cast=bool)

# Define ALLOWED_HOSTS based on environment using python-decouple
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,5b57-86-46-100-229.ngrok-free.app' if DEBUG else 'www.jwalshedev.ie', 
    cast=Csv()
)

# Define Google Redirect URI based on environment using python-decouple
GOOGLE_REDIRECT_URI = 'http://localhost:8000/oauth2callback/' if DEBUG else 'https://www.jwalshedev.ie/jobs/oauth2callback/'

# Security settings
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Retrieve environment variables using python-decouple
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='')
SECRET_KEY = config('SECRET_KEY', default='default-secret-key')
DATABASE_URL = config('DATABASE_URL', default='')
GMAIL_TOKEN_JSON = config('GMAIL_TOKEN_JSON', default='')

# Log environment variable values (excluding sensitive information where necessary)
logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
logger.debug(f"GOOGLE_CLIENT_SECRET: {'REDACTED' if GOOGLE_CLIENT_SECRET else 'Not set'}")
logger.debug(f"GOOGLE_API_KEY: {'REDACTED' if GOOGLE_API_KEY else 'Not set'}")
logger.debug(f"SECRET_KEY: {'REDACTED' if SECRET_KEY else 'Not set'}")
logger.debug(f"DATABASE_URL: {'REDACTED' if DATABASE_URL else 'Not set'}")
logger.debug(f"GMAIL_TOKEN_JSON: {'REDACTED' if GMAIL_TOKEN_JSON else 'Not set'}")

# Define Token File Path
TOKEN_FILE_PATH = BASE_DIR / 'token.json'

# Function to get Google credentials from environment variable
def get_google_credentials():
    if not GMAIL_TOKEN_JSON:
        logger.error("GMAIL_TOKEN_JSON environment variable not found.")
        raise EnvironmentError("GMAIL_TOKEN_JSON environment variable not found.")
    try:
        credentials = json.loads(GMAIL_TOKEN_JSON)
        logger.debug(f"GOOGLE_CREDENTIALS loaded: {credentials}")
        return credentials
    except json.JSONDecodeError as e:
        logger.error("Error decoding GMAIL_TOKEN_JSON: %s", e)
        raise ValueError("Error decoding GMAIL_TOKEN_JSON") from e

# Save token to a file
def save_token_to_file(token_info):
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(token_info, f)

# View to display token information
def token_file_view(request):
    if TOKEN_FILE_PATH.is_file():
        with open(TOKEN_FILE_PATH) as f:
            token_info = json.load(f)
        return HttpResponse(f"Token info: {json.dumps(token_info, indent=2)}")
    return HttpResponse("Token file not found.")

# Retrieve or refresh access token
def get_access_token():
    if TOKEN_FILE_PATH.is_file():
        with open(TOKEN_FILE_PATH) as f:
            token_info = json.load(f)
        if 'access_token' in token_info and 'expiry' in token_info:
            expiry = datetime.fromisoformat(token_info['expiry'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) < expiry:
                return token_info['access_token']
    
    credentials = get_google_credentials()
    refresh_token = credentials.get('refresh_token')
    if not refresh_token:
        logger.error("Refresh token is missing.")
        raise ValueError("Refresh token is missing.")

    token_info = refresh_google_token(refresh_token)
    token_info['expiry'] = (datetime.now(timezone.utc) + timedelta(seconds=token_info['expires_in'])).isoformat()
    save_token_to_file(token_info)
    return token_info['access_token']

# Refresh Google token when it expires
def refresh_google_token(refresh_token):
    response = requests.post(
        'https://oauth2.googleapis.com/token',  # TOKEN_URI should be defined or hardcoded
        data={
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to refresh token: {response.content.decode('utf-8')}")
        response.raise_for_status()

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
        if http_err.response.status_code == 401:
            logger.info("Access token expired, refreshing token...")
            token = get_access_token()
            headers['Authorization'] = f'Bearer {token}'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    return None

# Get information about the current token
def get_token_info(token):
    response = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}')
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to get token info: {response.text}")
        return None

# Django view to display environment variable
def env_view(request):
    google_credentials_json = config('GMAIL_TOKEN_JSON', default='{}')
    return HttpResponse(f"GMAIL_TOKEN_JSON: {google_credentials_json}")

# Check if the app is running on Heroku
HEROKU = 'DYNO' in os.environ

if HEROKU:  # Heroku environment
    logger.debug(f"GMAIL_TOKEN_JSON from environment: {config('GMAIL_TOKEN_JSON', default='')}")
else:  # Local environment
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / 'credentials.json'
    if not GOOGLE_CREDENTIALS_PATH.is_file():
        raise FileNotFoundError(f"File not found: {GOOGLE_CREDENTIALS_PATH}")
    try:
        with open(GOOGLE_CREDENTIALS_PATH) as f:
            GOOGLE_CREDENTIALS = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON from file") from e

# Extract values from credentials or environment
GOOGLE_CREDENTIALS = get_google_credentials()
GOOGLE_CLIENT_ID = GOOGLE_CREDENTIALS.get('client_id')
GOOGLE_CLIENT_SECRET = GOOGLE_CREDENTIALS.get('client_secret')
GOOGLE_API_KEY = config('GOOGLE_API_KEY', default="")

logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
logger.debug(f"GOOGLE_CLIENT_SECRET: {'REDACTED' if GOOGLE_CLIENT_SECRET else 'Not set'}")

# Database configuration
if HEROKU:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL', default=''),
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

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS', 
    default='https://www.jwalshedev.ie,https://johnsite.herokuapp.com,https://5b57-86-46-100-229.ngrok-free.app', 
    cast=Csv()
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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


