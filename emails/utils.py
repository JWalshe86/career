import os
import json
import logging
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from django.utils.functional import SimpleLazyObject
from django.utils import timezone
from django.conf import settings
from oauth.models import OAuthToken
from google_auth_oauthlib.flow import InstalledAppFlow

# Setup logging
logger = logging.getLogger(__name__)



from google.oauth2.credentials import Credentials
import json
import os
from django.conf import settings  # Ensure you import the settings


from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.utils.functional import SimpleLazyObject

def get_unread_emails(creds):
    """Fetch unread emails using the provided credentials."""
    try:
        # Log what is being passed into the function
        logger.debug(f"Received creds of type: {type(creds)}")
        logger.debug(f"Received creds content: {creds}")

        # Ensure the credentials are of the correct type
        if not isinstance(creds, Credentials):
            logger.error(f"Invalid credentials object type: {type(creds)}")
            raise TypeError("Invalid credentials object type")

        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Fetch unread emails from the user's inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])

        unread_emails = []
        # Extract details from each unread email message
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
            # Append only if both subject and sender are found
            if email_info['subject'] and email_info['sender']:
                unread_emails.append(email_info)

        # Log the number of unread emails retrieved
        logger.debug(f"Retrieved {len(unread_emails)} unread emails.")
        return unread_emails, None

    except Exception as e:
        logger.error(f"Error fetching unread emails: {e}", exc_info=True)
        return None, str(e)

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

def refresh_credentials(creds):
    """Refresh credentials if expired."""
    logger.debug(f"Checking if credentials are expired: Expiry time: {creds.expiry if creds else 'No credentials'}")
    if creds and creds.expired and creds.refresh_token:
        logger.debug("Credentials are expired. Refreshing...")
        try:
            creds.refresh(Request())
            logger.debug(f"Credentials refreshed successfully. New expiry time: {creds.expiry}")
            return creds
        except RefreshError as e:
            logger.error(f"Error refreshing credentials: {e}")
            raise
    logger.debug("Credentials are still valid.")
    return creds

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

