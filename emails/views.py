import os
import json
import logging
from django.shortcuts import render, redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError

# Setup logger
logger = logging.getLogger(__name__)

def get_unread_emails():
    """
    Fetch unread emails for the authenticated user.

    :return: Tuple (emails, auth_url)
    """
    try:
        # Determine if running on Heroku
        if os.getenv('HEROKU'):
            # Load credentials from TOKEN_JSON_CONTENT environment variable
            token_json_content = os.getenv('TOKEN_JSON_CONTENT')
            if token_json_content:
                credentials_data = json.loads(token_json_content)
            else:
                raise ValueError("TOKEN_JSON_CONTENT environment variable is not set.")
        else:
            # Load credentials from token.json file when running locally
            token_json_path = os.getenv('TOKEN_JSON_PATH', 'token.json')
            with open(token_json_path, 'r') as token_file:
                credentials_data = json.load(token_file)

        # Create Credentials object from loaded data
        creds = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # List messages in the user's inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])

        emails = []
        if not messages:
            emails.append({'date': '', 'sender': '', 'snippet': 'No unread messages found.'})
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg.get('payload', {}).get('headers', [])
                
                # Extracting necessary fields
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No Date')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No Sender')
                snippet = msg.get('snippet', '')

                # Append to emails list
                emails.append({'date': date, 'sender': sender, 'snippet': snippet})

        return emails, None

    except GoogleAuthError as auth_error:
        logger.error(f"Google Authentication Error: {auth_error}")
        return [], "Authentication Error"
    except ValueError as val_error:
        logger.error(f"Value Error: {val_error}")
        return [], "Value Error"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return [], "Unexpected Error"


def email_dashboard(request):
    """Render email dashboard with unread emails."""
    logger.debug("Rendering email dashboard.")

    email_subjects, auth_url = get_unread_emails()
    if auth_url:
        logger.debug(f"Redirecting to authorization URL: {auth_url}")
        return redirect(auth_url)

    unread_email_count = len(email_subjects) if email_subjects else 0

    # Debugging output
    logger.debug(f"Unread email count: {unread_email_count}")

    context = {
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
    }
    logger.debug(f"Context for rendering: {context}")
    return render(request, "emails/email_dashboard.html", context)

