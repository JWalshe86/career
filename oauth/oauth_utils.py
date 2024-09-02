# oauth/oauth_utils.py

import json
import logging
import os
from django.conf import settings
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError  
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2 import InsecureTransportError
from google.auth.exceptions import GoogleAuthError

logger = logging.getLogger(__name__)

# Define the scopes you need
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'token.json')


def get_unread_emails():
    creds = None
    auth_url = None

    if 'DYNO' in os.environ:  # Heroku environment
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        try:
            google_credentials = json.loads(google_credentials_json)
            creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
            logger.debug("Loaded credentials from environment variables.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for Google credentials: {e}")
            return [], None
    else:  # Local environment
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.debug("Loaded credentials from token.json.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token.json.")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            if not 'DYNO' in os.environ:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            logger.info("Credentials refreshed and saved.")
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            auth_url = get_oauth2_authorization_url()
            return [], auth_url

    if not creds or not creds.valid:
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

def get_oauth2_authorization_url():
    """Generate OAuth2 authorization URL."""
    logger.debug("Generating OAuth2 authorization URL.")
    try:
        if 'DYNO' in os.environ:  # Heroku environment
            google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
            credentials = json.loads(google_credentials_json)
            flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
        else:  # Local environment
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS_PATH,
                SCOPES
            )
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise


def get_google_credentials():
    """Retrieve Google credentials based on environment."""
    if 'DYNO' in os.environ:  # Heroku environment
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON', '{}')
    else:  # Local development
        credentials_file_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if not os.path.isfile(credentials_file_path):
            raise FileNotFoundError(f"File not found: {credentials_file_path}")
        with open(credentials_file_path) as f:
            credentials_json = f.read()
    
    try:
        credentials = json.loads(credentials_json)
        logger.debug(f"GOOGLE_CREDENTIALS loaded: {credentials}")
        return credentials
    except json.JSONDecodeError as e:
        logger.error("Error decoding GOOGLE_CREDENTIALS_JSON: %s", e)
        raise ValueError("Error decoding GOOGLE_CREDENTIALS_JSON") from e

def save_token_to_file(token_info):
    """Save token information to a file."""
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(token_info, f)

def get_access_token():
    """Retrieve or refresh access token."""
    if os.path.isfile(TOKEN_FILE_PATH):
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

