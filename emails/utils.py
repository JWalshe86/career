import os
import json
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from django.http import HttpResponse
from django.shortcuts import render
from oauth.oauth_utils import exchange_code_for_tokens

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_credentials():
    """Load credentials from the environment or a file."""
    if 'TOKEN_JSON_CONTENT' in os.environ:
        token_json_content = os.getenv('TOKEN_JSON_CONTENT')
        logger.debug("Loading credentials from environment variable.")
        try:
            credentials_data = json.loads(token_json_content)
            logger.debug(f"Loaded credentials data: {credentials_data}")
            return credentials_data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from TOKEN_JSON_CONTENT: {e}", exc_info=True)
            raise
    else:
        logger.debug("Running locally.")
        token_json_path = os.getenv('TOKEN_JSON_PATH', 'token.json')
        try:
            with open(token_json_path, 'r') as token_file:
                logger.debug(f"Loading credentials from {token_json_path}.")
                credentials_data = json.load(token_file)
                logger.debug(f"Loaded credentials data: {credentials_data}")
                return credentials_data
        except FileNotFoundError as e:
            logger.error(f"Token file not found: {e}", exc_info=True)
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from token file: {e}", exc_info=True)
            raise

def create_credentials(credentials_data):
    """Create Credentials object from credentials data."""
    logger.debug(f"Creating credentials with data: {credentials_data}")
    try:
        creds = Credentials(
            token=credentials_data.get('token'),
            refresh_token=credentials_data.get('refresh_token'),
            token_uri=credentials_data.get('token_uri'),
            client_id=credentials_data.get('client_id'),
            client_secret=credentials_data.get('client_secret'),
            scopes=credentials_data.get('scopes')
        )
        logger.debug(f"Credentials created: {creds}")
        return creds
    except Exception as e:
        logger.error(f"Error creating credentials: {e}", exc_info=True)
        raise

def refresh_credentials(creds):
    """Refresh credentials if expired."""
    logger.debug(f"Checking if credentials are expired. Type: {type(creds)}")
    if creds.expired:
        logger.debug("Credentials are expired. Refreshing...")
        try:
            creds.refresh(Request())
            logger.debug("Credentials refreshed successfully.")
        except RefreshError as e:
            logger.error(f"Error refreshing credentials: {e}", exc_info=True)
            raise
    return creds

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_unread_emails(auth_code=None, user=None):
    """
    Fetch unread emails from Gmail.
    
    Args:
        auth_code (str, optional): The authorization code received from the OAuth2 flow.
        user (User, optional): The user object to load credentials for.
    
    Returns:
        tuple: A tuple containing a list of unread emails and an authorization URL if needed.
    """
    creds = None
    auth_url = None

    if auth_code:
        try:
            creds = exchange_code_for_tokens(auth_code)
            save_credentials_to_db(user, creds)  # Save new credentials
        except Exception as e:
            logger.error(f"Error handling authorization code: {e}")
            return [], None

    if creds:
        creds = refresh_tokens(creds, user)
        if not creds:
            auth_url = get_oauth2_authorization_url()
            return [], auth_url
    else:
        creds = load_credentials_from_db(user)
        if creds:
            creds = refresh_tokens(creds, user)
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



def parse_messages(messages, service):
    """Parse email messages to extract relevant details."""
    emails = []
    if not messages:
        emails.append({'date': '', 'sender': '', 'snippet': 'No unread messages found.'})
    else:
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg.get('payload', {}).get('headers', [])
                
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No Date')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No Sender')
                snippet = msg.get('snippet', '')

                logger.debug(f"Email details - Subject: {subject}, Date: {date}, Sender: {sender}, Snippet: {snippet}")

                emails.append({'date': date, 'sender': sender, 'snippet': snippet})
            except Exception as e:
                logger.error(f"Error parsing message with id {message['id']}: {e}", exc_info=True)
    return emails

def display_emails(request):
    """Render the section of the main dashboard showing unread emails."""
    logger.debug("Rendering display emails section.")

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated.")
        return HttpResponse("User must be logged in to access this page.", status=403)

    # Initialize service with credentials
    try:
        credentials_data = load_credentials()
        logger.debug(f"Loaded credentials data: {credentials_data}")

        creds = create_credentials(credentials_data)
        logger.debug(f"Type of creds: {type(creds)}")
        logger.debug(f"Credentials content: {creds}")

        creds = refresh_credentials(creds)
        logger.debug("Credentials refreshed successfully.")

        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.debug("Gmail API service built successfully.")
        except Exception as e:
            logger.error(f"Error building Gmail API service: {e}", exc_info=True)
            return HttpResponse("Failed to build Gmail API service.", status=500)

        email_subjects, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error occurred while fetching emails: {error}")
            return HttpResponse(f"An error occurred while fetching emails: {error}", status=500)

        unread_email_count = len(email_subjects) if email_subjects else 0

        context = {
            'email_subjects': email_subjects,
            'unread_email_count': unread_email_count,
        }
        return render(request, "emails/display_emails.html", context)

    except RefreshError as e:
        logger.error(f"Error during credential refresh: {e}", exc_info=True)
        return HttpResponse("Credentials could not be refreshed. Please re-authenticate.", status=401)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return HttpResponse("An unexpected error occurred. Please try again later.", status=500)

