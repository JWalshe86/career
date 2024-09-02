import json
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2 import InsecureTransportError
from google.auth.exceptions import GoogleAuthError, RefreshError
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'token.json')

def refresh_tokens(creds: Credentials):
    """Refresh OAuth2 tokens if expired."""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials back to file
            with open(TOKEN_FILE_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            logger.info("Credentials refreshed and saved.")
        return creds
    except RefreshError as e:
        logger.error(f"Token refresh error: {e}")
        return None


def get_oauth2_authorization_url():
    """Generate OAuth2 authorization URL."""
    logger.debug("Generating OAuth2 authorization URL.")
    try:
    if 'DYNO' in os.environ:
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        logger.debug(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")
        credentials_data = json.loads(google_credentials_json)
        
        # Check if the JSON is correctly structured
        if 'installed' not in credentials_data and 'web' not in credentials_data:
            logger.error(f"Invalid client secrets format: {credentials_data}")
            raise ValueError("Invalid client secrets format. Must contain 'installed' or 'web'.")
        
        flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE_CREDENTIALS_PATH, SCOPES)
    
    auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    logger.info(f"Generated authorization URL: {auth_url}")
    return auth_url
except Exception as e:
    logger.error(f"Error generating authorization URL: {e}")
    raise


def get_unread_emails():
    """Fetch unread emails from Gmail."""
    creds = None
    auth_url = None

    if 'DYNO' in os.environ:
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        try:
            google_credentials = json.loads(google_credentials_json)
            creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
            logger.debug("Loaded credentials from environment variables.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for Google credentials: {e}")
            return [], None
    else:
        if os.path.exists(TOKEN_FILE_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
            logger.debug("Loaded credentials from token.json.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE_PATH, 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token.json.")

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
    except HttpError as error:
        logger.error(f"An error occurred while fetching emails: {error}")
        return [], None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return [], None

