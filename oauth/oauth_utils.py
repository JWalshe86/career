from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

# Path to store the token
TOKEN_FILE_PATH = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def exchange_code_for_tokens(auth_code):
    """Exchange the authorization code for tokens."""
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': auth_code,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
            'grant_type': 'authorization_code'
        }
    )
    tokens = response.json()
    if 'error' in tokens:
        logger.error(f"Error exchanging code for tokens: {tokens['error_description']}")
        raise Exception("Error exchanging code for tokens")
    return tokens

def refresh_tokens(creds):
    """Refresh OAuth2 tokens."""
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
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        credentials_data = json.loads(google_credentials_json)

        if 'web' not in credentials_data:
            logger.error(f"Invalid client secrets format: {credentials_data}")
            raise ValueError("Invalid client secrets format. Must contain 'web'.")

        flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

def get_unread_emails(auth_code=None):
    """Fetch unread emails from Gmail."""
    creds = None
    auth_url = None

    if auth_code:
        try:
            tokens = exchange_code_for_tokens(auth_code)
            google_credentials = {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "refresh_token": tokens.get('refresh_token'),
                "token_uri": "https://oauth2.googleapis.com/token"
            }
            creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
            # Save credentials to file
            with open(TOKEN_FILE_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            logger.info("Saved new credentials to token.json.")
        except Exception as e:
            logger.error(f"Error handling authorization code: {e}")
            return [], None

    if creds:
        creds = refresh_tokens(creds)
        if not creds:
            auth_url = get_oauth2_authorization_url()
            return [], auth_url
    else:
        if os.path.exists(TOKEN_FILE_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
            logger.debug("Loaded credentials from token.json.")
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

