from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import GoogleAuthError
import logging
import os
import json
from django.shortcuts import render, redirect

# Setup logger
logger = logging.getLogger(__name__)

# emails/views.py


def get_unread_emails(user):
    try:
        # Determine if we're running in a production environment
        is_production = not settings.DEBUG

        # Check if TOKEN_JSON_CONTENT environment variable is set
        token_json_content = os.getenv('TOKEN_JSON_CONTENT')
        if token_json_content:
            # Use the JSON content from the environment variable
            token_data = json.loads(token_json_content)
        else:
            # Fall back to reading from TOKEN_JSON_PATH if TOKEN_JSON_CONTENT is not set
            token_json_path = os.getenv('TOKEN_JSON_PATH')
            if not token_json_path:
                raise FileNotFoundError('TOKEN_JSON_PATH environment variable is not set.')

            # Read the contents of the token.json file
            with open(token_json_path, 'r') as token_file:
                token_data = json.load(token_file)

        # Create the credentials from the JSON data
        creds = Credentials.from_authorized_user_info(token_data)
        service = build('gmail', 'v1', credentials=creds)

        # Fetch unread emails
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])

        email_subjects = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
            email_subjects.append(msg['snippet'])

        return email_subjects, None

    except GoogleAuthError as error:
        logger.error(f"An error occurred with Google Auth: {error}")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return None, None



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

