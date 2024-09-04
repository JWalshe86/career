import json
import logging
from django.utils import timezone
from .models import OAuthToken
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Setup logging
logger = logging.getLogger(__name__)

def load_credentials_from_db(user):
    """
    Load credentials from the database for a given user.
    
    Args:
        user (User): The user object to load credentials for.
    
    Returns:
        Credentials: Loaded credentials if available and not expired, otherwise None.
    """
    try:
        token_record = OAuthToken.objects.get(user=user)
        if token_record.expiry < timezone.now():
            # Token is expired
            return None

        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes
        )
        return creds
    except OAuthToken.DoesNotExist:
        # No token found
        return None
    except Exception as e:
        logger.error(f"Error loading credentials from database: {e}")
        return None

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

def get_unread_emails(auth_code=None):
    """
    Fetch unread emails from Gmail.
    
    Args:
        auth_code (str, optional): The authorization code received from the OAuth2 flow.
    
    Returns:
        tuple: A tuple containing a list of unread emails and an authorization URL if needed.
    """
    creds = None
    auth_url = None

    if auth_code:
        try:
            creds = exchange_code_for_tokens(auth_code)
        except Exception as e:
            logger.error(f"Error handling authorization code: {e}")
            return [], None

    if creds:
        creds = refresh_tokens(creds)
        if not creds:
            auth_url = get_oauth2_authorization_url()
            return [], auth_url
    else:
        creds = load_credentials_from_db(user)  # Make sure to pass the user object here
        if creds:
            creds = refresh_tokens(creds)
            if not creds:
                auth_url = get_oauth2_authorization_url()
                return [], auth_url
        else:
            logger.debug("No valid credentials found. Redirecting to authorization URL.")
            auth_url = get_oauth2_authorization_url()
            return [], auth_url

    try:
        service = build("gmail", "v1", credentials=creds)
        excluded_senders = [
            "no-reply@usebubbles.com",
            "chandeep@2toucans.com",
            "craig@itcareerswitch.co.uk",
            "no-reply@swagapp.com",
            "no-reply@fathom.video",
            "mailer@jobleads.com",
            "careerservice@email.jobleads.com"
        ]
        query = "is:unread -category:social -category:promotions"
        for sender in excluded_senders:
            query += f" -from:{sender}"
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get('messages', [])

        unread_emails = []
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            snippet = msg['snippet']
            email_data = {
                'id': message['id'],
                'snippet': snippet,
                'sender': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'),
                'subject': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'),
                'highlight': 'highlight' if 'unfortunately' in snippet.lower() else ''
            }
            unread_emails.append(email_data)

        logger.info(f"Processed unread emails: {unread_emails}")
        return unread_emails, None
    except Exception as e:
        logger.error(f"An error occurred while fetching emails: {e}")
        return [], None

import json
import logging
import requests
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request

# Setup logging
logger = logging.getLogger(__name__)

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

def refresh_tokens(creds):
    """
    Refresh OAuth2 tokens if they are expired.
    
    Args:
        creds (Credentials): The credentials to refresh.
    
    Returns:
        Credentials: Refreshed credentials or None if refresh failed.
    """
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials_to_db(user, creds)  # Ensure 'user' is available
            logger.info("Credentials refreshed and saved.")
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
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": "johnsite-433520",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, scopes=settings.SCOPES)
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        logger.info(f"Generated authorization URL: {authorization_url}")
        return authorization_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

