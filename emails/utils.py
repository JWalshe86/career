import os
import django
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

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to get user by username
def get_user(username):
    logger.debug(f"Fetching user: {username}")
    try:
        user = User.objects.get(username=username)
        logger.debug(f"User found: {user}")
        return user
    except User.DoesNotExist:
        logger.error(f"User '{username}' not found.")
        return None

# Function to load credentials
def load_credentials(user):
    try:
        token_record = OAuthToken.objects.get(user=user)
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id='your_client_id',  # Replace with actual client ID
            client_secret='your_client_secret',  # Replace with actual client secret
            scopes=['your_scopes'],  # Replace with actual scopes
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

# Function to fetch unread emails
def get_unread_emails(creds):
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

# OAuth Flow Example
def handle_oauth_callback(auth_code, username):
    """Handle the OAuth callback to exchange the auth code for tokens and fetch unread emails."""
    user = get_user(username)
    if not user:
        logger.error(f"User '{username}' not found.")
        return

    # Exchange auth code for tokens (you need to implement this)
    creds = exchange_code_for_tokens(auth_code)
    if creds:
        # Save credentials to database
        save_credentials_to_db(user, creds)
        
        # Fetch unread emails
        unread_emails, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error fetching unread emails: {error}")
        else:
            logger.info("Unread Emails:", unread_emails)
    else:
        logger.error("Failed to obtain credentials.")

# Add the exchange_code_for_tokens and save_credentials_to_db functions
# ...

# Entry point if needed
if __name__ == "__main__":
    # Simulate handling an OAuth callback
    handle_oauth_callback('your_auth_code', 'johnwalshe')  # Change the username as needed



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
    """Save credentials to the database for a given user."""
    save_credentials_to_db(user, creds)


from django.utils import timezone
from datetime import datetime
import pytz  # Ensure you have pytz installed

def save_credentials_to_db(user, creds):
    """Save credentials to the database for a given user."""
    try:
        # Create or get the existing OAuthToken record for the user
        token_record, created = OAuthToken.objects.get_or_create(user=user)
        
        # Save the token details
        token_record.access_token = creds.token
        token_record.refresh_token = creds.refresh_token
        token_record.token_uri = creds.token_uri
        token_record.client_id = creds.client_id
        token_record.client_secret = creds.client_secret
        token_record.scopes = ','.join(creds.scopes)  # Store scopes as a comma-separated string

        # Define your timezone (adjust as necessary)
        your_timezone = pytz.timezone('UTC')  # Change 'UTC' to your desired timezone if needed
        
        # Check if expiry is set correctly
        if creds.expiry:
            # Create a timezone-aware expiry datetime
            token_record.expiry = timezone.make_aware(creds.expiry)  # Ensure expiry is timezone-aware
        else:
            # If no expiry is set, default to 1 hour from now
            token_record.expiry = timezone.now() + timezone.timedelta(seconds=3600)

        # Save the token record to the database
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

