import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decouple import config, Csv
from dotenv import load_dotenv
import dj_database_url
from django.http import HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError

# Load environment variables from .env file (for local development)
load_dotenv()

# Set debug mode
DEBUG = config('DEBUG', default=False, cast=bool)
ROOT_URLCONF = 'career.urls'  # Adjust according to your project name
print(f"DEBUG from .env: {os.getenv('DEBUG')}")
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Retrieve settings
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,5b57-86-46-100-229.ngrok-free.app,johnsite-d251709cf12b.herokuapp.com,www.jwalshedev.ie', cast=Csv())
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='https://www.jwalshedev.ie/jobs/oauth2callback')
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Retrieve environment variables
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
    """Retrieve Google credentials based on environment."""
    if 'DYNO' in os.environ:  # Heroku environment
        credentials_json = GOOGLE_CREDENTIALS_JSON
    else:  # Local development
        credentials_file_path = BASE_DIR / 'credentials.json'
        if not credentials_file_path.is_file():
            raise FileNotFoundError(f"File not found: {credentials_file_path}")
        with open(credentials_file_path) as f:
            credentials_json = f.read()
    
    try:
        credentials = json.loads(GMAIL_TOKEN_JSON)
        logger.debug(f"GOOGLE_CREDENTIALS loaded: {credentials}")
        return credentials
    except json.JSONDecodeError as e:
        logger.error("Error decoding GOOGLE_CREDENTIALS_JSON: %s", e)
        raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON") from e


def get_oauth2_authorization_url():
    try:
        if settings.DEBUG:
            credentials_path = settings.GOOGLE_CREDENTIALS_PATH
            with open(credentials_path, 'r') as file:
                credentials = json.load(file)
        else:
            credentials = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        
        # Initialize OAuth2 flow
        flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return None


def save_token_to_file(token_info):
    """Save token information to a file."""
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(token_info, f)

def get_access_token():
    """Retrieve or refresh access token."""
    if TOKEN_FILE_PATH.is_file():
        with open(TOKEN_FILE_PATH) as f:
            token_info = json.load(f)
        if 'access_token' in token_info and 'expiry' in token_info:
            expiry = datetime.fromisoformat(token_info['expiry'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) < expiry:
                return token_info['access_token']
    
    # Fetch new credentials
    credentials = get_google_credentials()
    refresh_token = credentials.get('refresh_token')
    if not refresh_token:
        raise ValueError("Refresh token is missing.")
    
    try:
        token_info = refresh_google_token(refresh_token)
        token_info['expiry'] = (datetime.now(timezone.utc) + timedelta(seconds=token_info['expires_in'])).isoformat()
        save_token_to_file(token_info)
        return token_info['access_token']
    except RefreshError as e:
        logger.error(f"Refresh token error: {e}")
        auth_url = get_oauth2_authorization_url()
        if auth_url:
            logger.info(f"Please visit this URL to re-authenticate: {auth_url}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token retrieval: {e}")
        raise

def refresh_google_token(refresh_token):
    """Refresh Google OAuth2 token using the refresh token."""
    try:
        creds = Credentials(
            refresh_token=refresh_token,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            token=None  # Initial token is None
        )
        creds.refresh(Request())
        token_info = {
            'access_token': creds.token,
            'expires_in': (creds.expiry.timestamp() - datetime.now(timezone.utc).timestamp()),
            'expiry': creds.expiry.isoformat()
        }
        save_token_to_file(token_info)
        return token_info
    except RefreshError as e:
        logger.error(f"Refresh token error: {e}")
        # Trigger re-authentication if refresh fails
        auth_url = get_oauth2_authorization_url()
        if auth_url:
            logger.info(f"Please visit this URL to re-authenticate: {auth_url}")
        # Clear token file if refresh fails
        if TOKEN_FILE_PATH.is_file():
            os.remove(TOKEN_FILE_PATH)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise

def make_google_api_request(url, token):
    """Make an API request to Google services using the access token."""
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
            # Access token may be expired or invalid
            token = get_access_token()  # Refresh token and retry
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

def get_token_info(token):
    """Get information about the current token."""
    response = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}')
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to get token info: {response.text}")
        return None

def env_view(request):
    """Django view to display environment variable."""
    google_credentials_json = GOOGLE_CREDENTIALS_JSON
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

def token_file_view(request):
    """Django view to display token information."""
    if TOKEN_FILE_PATH.is_file():
        with open(TOKEN_FILE_PATH) as f:
            token_info = json.load(f)
        return HttpResponse(f"Token info: {json.dumps(token_info, indent=2)}")
    return HttpResponse("Token file not found.")

# Heroku detection
HEROKU = 'DYNO' in os.environ

# Check if running in production (Heroku)
IS_HEROKU = 'DYNO' in os.environ

# Define GOOGLE_CREDENTIALS
# Define GOOGLE_CREDENTIALS
if IS_HEROKU:
    GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if GOOGLE_CREDENTIALS_JSON:
        GOOGLE_CREDENTIALS = json.loads(GOOGLE_CREDENTIALS_JSON)
    else:
        GOOGLE_CREDENTIALS = {}
else:
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / 'credentials.json'



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

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Static files storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Ensure this is the correct path to your static files

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
        'DIRS': [BASE_DIR / 'templates'],  # Ensure this path is correct
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'jobs.context_processors.unread_email_count',  # Ensure this path is correct
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

