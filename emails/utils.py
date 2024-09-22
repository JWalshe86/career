import os
import json
import logging
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from django.conf import settings
from oauth.models import OAuthToken
from google_auth_oauthlib.flow import InstalledAppFlow
from django.contrib.auth.models import User
# Setup logging
logger = logging.getLogger(__name__)

def get_user(username):
    """Retrieve a user instance by username."""
    logger.debug(f"Fetching user: {username}")
    try:
        user = User.objects.get(username=username)
        logger.debug(f"User found: {user}")
        return user
    except User.DoesNotExist:
        logger.error(f"User '{username}' not found.")
        return None


def get_unread_emails(creds):
    """Fetch unread emails using the provided credentials."""
    try:
        logger.debug(f"Received creds of type: {type(creds)}")
        if not isinstance(creds, Credentials):
            logger.error(f"Invalid credentials object type: {type(creds)}")
            raise TypeError("Invalid credentials object type")

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])

        unread_emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            email_info = {
                'subject': None,
                'sender': None,
                'snippet': msg.get('snippet', '')
            }
            for values in email_data:
                if values['name'] == 'Subject':
                    email_info['subject'] = values['value']
                elif values['name'] == 'From':
                    email_info['sender'] = values['value']
            if email_info['subject'] and email_info['sender']:
                unread_emails.append(email_info)

        logger.debug(f"Retrieved {len(unread_emails)} unread emails.")
        return unread_emails, None

    except Exception as e:
        logger.error(f"Error fetching unread emails: {e}", exc_info=True)
        return None, str(e)

def exchange_code_for_tokens(auth_code):
    """Exchange the authorization code for tokens."""
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

def refresh_credentials(creds):
    """Refresh credentials if expired."""
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.debug(f"Credentials refreshed successfully. New expiry time: {creds.expiry}")
            return creds
        except RefreshError as e:
            logger.error(f"Error refreshing credentials: {e}")
            raise
    return creds

def get_oauth2_authorization_url():
    """Generate OAuth2 authorization URL."""
    try:
        client_config = {
            "installed": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, scopes=settings.SCOPES)
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        logger.info(f"Generated authorization URL: {authorization_url}")
        return authorization_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

def save_credentials(user, creds):
    """Save credentials to either a local file or the database depending on the environment."""
    if settings.DEBUG:
        save_credentials_to_file(creds)
    else:
        save_credentials_to_db(user, creds)

def load_credentials(user):
    """Load credentials either from a local file or from the database depending on the environment."""
    if settings.DEBUG:
        return load_credentials_from_file()
    else:
        return load_credentials_from_db(user)

def save_credentials_to_file(creds):
    """Save credentials to a local token.json file."""
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    with open('token.json', 'w') as token_file:
        json.dump(token_data, token_file)
    logger.info("Credentials saved to token.json locally.")


def load_credentials_from_file():
    """Load credentials from a local token.json file."""
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            token_data = json.load(token_file)
            creds = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),  # Use .get to avoid KeyError
                token_uri='https://oauth2.googleapis.com/token',  # Set a default value
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=settings.SCOPES,
                expiry=None  # Set to None if you don't have expiry info
            )
            logger.info("Credentials loaded from token.json.")
            return creds
    else:
        logger.error("token.json file not found.")
        return None


def save_credentials_to_db(user, creds):
    """Save credentials to the database for a given user."""
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

def load_credentials_from_db(user):
    """Load credentials from the database for a given user."""
    try:
        token_record = OAuthToken.objects.get(user=user)
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes,
            expiry=token_record.expiry
        )
        logger.info("Credentials loaded from database.")
        return creds
    except OAuthToken.DoesNotExist:
        logger.error("OAuthToken record not found for user.")
        return None
    except Exception as e:
        logger.error(f"Error loading credentials from database: {e}")
        return None

