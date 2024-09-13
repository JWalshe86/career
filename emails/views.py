import os
import json
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_credentials():
    """Load credentials from the environment or a file."""
    if 'TOKEN_JSON_CONTENT' in os.environ:
        token_json_content = os.getenv('TOKEN_JSON_CONTENT')
        logger.debug("Loading credentials from environment variable.")
        return json.loads(token_json_content)
    else:
        logger.debug("Running locally.")
        token_json_path = os.getenv('TOKEN_JSON_PATH', 'token.json')
        with open(token_json_path, 'r') as token_file:
            logger.debug(f"Loading credentials from {token_json_path}.")
            return json.load(token_file)

def create_credentials(credentials_data):
    """Create Credentials object from credentials data."""
    logger.debug(f"Creating credentials with data: {credentials_data}")
    return Credentials(
        token=credentials_data.get('token'),
        refresh_token=credentials_data.get('refresh_token'),
        token_uri=credentials_data.get('token_uri'),
        client_id=credentials_data.get('client_id'),
        client_secret=credentials_data.get('client_secret'),
        scopes=credentials_data.get('scopes')
    )

def refresh_credentials(creds):
    """Refresh credentials if expired."""
    logger.debug(f"Checking if credentials are expired.")
    if creds.expired:
        logger.debug("Credentials are expired. Refreshing...")
        try:
            creds.refresh(Request())
            logger.debug("Credentials refreshed successfully.")
        except RefreshError as e:
            logger.error(f"Error refreshing credentials: {e}")
            raise
    return creds

def get_unread_emails(creds):
    """Fetch unread emails using Gmail API."""
    try:
        service = build('gmail', 'v1', credentials=creds)
        logger.debug("Gmail API service built successfully.")

        query = 'is:unread -category:social -category:promotions -from:no-reply@usebubbles.com ' \
                '-from:chandeep@2toucans.com -from:info@email.meetup.com ' \
                '-from:craig@itcareerswitch.co.uk -from:no-reply@swagapp.com ' \
                '-from:no-reply@fathom.video -from:mailer@jobleads.com ' \
                '-from:careerservice@email.jobleads.com'
        logger.debug(f"Query built: {query}")

        results = service.users().messages().list(userId='me', q=query).execute()
        logger.debug(f"Gmail API response: {results}")

        messages = results.get('messages', [])
        logger.debug(f"Messages found: {len(messages)}")

        unread_emails = []
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                logger.debug(f"Message fetched: {msg['id']}")
                unread_emails.append(msg)
            except Exception as e:
                logger.error(f"Error fetching message with ID {message['id']}: {e}")

        return unread_emails, None

    except Exception as e:
        logger.error(f"Error fetching unread emails: {e}")
        return [], str(e)

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
                logger.error(f"Error parsing message with id {message['id']}: {e}")
    return emails

from django.shortcuts import render, redirect
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def display_emails(request):
    """Render the section of the main dashboard showing unread emails."""
    logger.debug("Rendering display emails section.")

    if not request.user.is_authenticated:
        return HttpResponse("User must be logged in to access this page.", status=403)

    # Initialize service with credentials
    try:
        credentials_data = load_credentials()
        creds = create_credentials(credentials_data)
        creds = refresh_credentials(creds)
        service = build('gmail', 'v1', credentials=creds)
        
        email_subjects, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error occurred: {error}")
            return HttpResponse(f"An error occurred: {error}", status=500)
        
        unread_email_count = len(email_subjects) if email_subjects else 0

        context = {
            'email_subjects': email_subjects,
            'unread_email_count': unread_email_count,
        }
        return render(request, "emails/display_emails.html", context)

    except RefreshError as e:
        logger.error(f"Error during credential refresh: {e}")
        # Redirect to an error page or provide a message
        return HttpResponse("Credentials could not be refreshed. Please re-authenticate.", status=401)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse("An unexpected error occurred. Please try again later.", status=500)

