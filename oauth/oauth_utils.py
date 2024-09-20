import json
import logging
import requests
from django.utils import timezone
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .models import OAuthToken
from google_auth_oauthlib.flow import InstalledAppFlow

# Setup logging
logger = logging.getLogger(__name__)

# def load_credentials_from_db(user):
#     """
#     Load credentials from the database for a given user.
    
#     Args:
#         user (User): The user object to load credentials for.
    
#     Returns:
#         Credentials: Loaded credentials if available and not expired, otherwise None.
#     """
#     try:
#         token_record = OAuthToken.objects.get(user=user)
#         if token_record.expiry < timezone.now():
#             # Token is expired
#             return None

#         creds = Credentials(
#             token=token_record.access_token,
#             refresh_token=token_record.refresh_token,
#             token_uri=token_record.token_uri,
#             client_id=token_record.client_id,
#             client_secret=token_record.client_secret,
#             scopes=token_record.scopes
#         )
#         return creds
#     except OAuthToken.DoesNotExist:
#         # No token found
#         return None
#     except Exception as e:
#         logger.error(f"Error loading credentials from database: {e}")
#         return None

def save_credentials_to_db(user, creds):
    """
    Save credentials to the database for a given user.
    
    Args:
        user (User): The user object to save credentials for.
        creds (Credentials): The credentials to save.
    """
    try:
        token_record, created = OAuthToken.objects.get_or_create(user=user)
        token_record.access_token = creds.token
        token_record.refresh_token = creds.refresh_token
        token_record.token_uri = creds.token_uri
        token_record.client_id = creds.client_id
        token_record.client_secret = creds.client_secret
        token_record.scopes = creds.scopes
        token_record.expiry = creds.expiry
        token_record.save()
        logger.info("Credentials saved to database.")
    except Exception as e:
        logger.error(f"Error saving credentials to database: {e}")


def exchange_code_for_tokens(auth_code):
    """
    Exchange the authorization code for tokens.
    
    Args:
        auth_code (str): The authorization code received from the OAuth2 flow.
    
    Returns:
        Credentials: Credentials object with the obtained tokens.
    
    Raises:
        Exception: If there is an error exchanging the code for tokens.
    """
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': auth_code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        tokens = response.json()
        if 'error' in tokens:
            logger.error(f"Error exchanging code for tokens: {tokens.get('error_description', 'No error description')}")
            raise Exception("Error exchanging code for tokens")
        
        creds = Credentials(
            token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            token_uri=tokens['token_uri'],
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.SCOPES
        )
        return creds
    except Exception as e:
        logger.error(f"Error during token exchange: {e}")
        raise

def refresh_tokens(creds, user):
    """
    Refresh OAuth2 tokens, optionally forcing a refresh even if not expired.

    Args:
        creds (Credentials): The credentials to refresh.
        user (User): The user whose credentials are to be updated.

    Returns:
        Credentials: Refreshed credentials or None if refresh failed.
    """
    logger.debug(f"Starting token refresh process for user: {user.username}")

    try:
        if creds:
            logger.debug("Credentials object exists.")
            
            # Force refresh even if not expired (testing mode)
            logger.debug("Forcing refresh regardless of expiration status.")
            if creds.refresh_token:
                logger.debug("Refresh token is available. Attempting to refresh...")
                creds.refresh(Request())  # Use the refresh token to get a new access token
                save_credentials_to_db(user, creds)
                logger.info("Credentials refreshed and saved successfully.")
            else:
                logger.debug("No refresh token available. Cannot refresh credentials.")
        else:
            logger.debug("No credentials object provided.")
        
        return creds
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return None

def get_oauth2_authorization_url():
    """
    Generate OAuth2 authorization URL.
    
    Returns:
        str: The authorization URL for OAuth2 login.
    
    Raises:
        Exception: If there is an error generating the authorization URL.
    """
    try:
        client_config = {
            "installed": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": "johnsite-433520",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }
        logger.debug(f"Client config: {json.dumps(client_config, indent=2)}")
        
        flow = InstalledAppFlow.from_client_config(client_config, scopes=settings.SCOPES)
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        logger.info(f"Generated authorization URL: {authorization_url}")
        return authorization_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

