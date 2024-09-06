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
    """
    Fetch unread emails for the authenticated user.
    
    :param user: Django user object (not used in this example but included for completeness)
    :return: Tuple (email_subjects, auth_url)
    """
    try:
        # Load credentials from environment variable
        token_json_content = os.getenv('TOKEN_JSON_CONTENT')
        if token_json_content:
            credentials_data = json.loads(token_json_content)
        else:
            raise ValueError("TOKEN_JSON_CONTENT environment variable is not set.")

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
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])

        email_subjects = []
        if not messages:
            email_subjects.append('No messages found.')
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_subjects.append(f"Message snippet: {msg['snippet']}")

        # No auth URL required here as credentials are directly used
        return email_subjects, None

    except Exception as e:
        return [], str(e)



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

#this works
# def get_unread_emails():
#     try:
#         # Hardcoded credentials
#         credentials_data = {
#             "token": "ya29.a0AcM612yfkQCayqMYT5-DN_xDnVTjjZrRZZY5yGP6JHRVZXzQRh5MImRNCIwOlIigSLtKICq8SLOTC1nbD1VQU1Ej5O4h6e5G_XeTiZVehPsVsU80WpBk8-IHkffv1clAb09EFz7F4FpEyjOsdVxwDcB10-1yPmeVZA2hFtS3xAaCgYKAfESARESFQHGX2MixNGe9x5k1BATXkE5ht7jvg0177",
#             "refresh_token": "1//09rLfVZGZF9plCgYIARAAGAkSNwF-L9IrQvgywgMQuI5zW-t8BEPNVv1_vbZNwQ9XhJ5b8HVN2Zr3Mnbix9ULtKGJcNqra5d6y6w",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "client_id": "554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com",
#             "client_secret": "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",
#             "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
#             "universe_domain": "googleapis.com",
#             "expiry": "2024-09-04T22:32:59.726508Z"
#         }

#         # Create Credentials object from loaded data
#         creds = Credentials(
#             token=credentials_data['token'],
#             refresh_token=credentials_data['refresh_token'],
#             token_uri=credentials_data['token_uri'],
#             client_id=credentials_data['client_id'],
#             client_secret=credentials_data['client_secret'],
#             scopes=credentials_data['scopes']
#         )

#         # Build the Gmail service
#         service = build('gmail', 'v1', credentials=creds)

#         # List messages in the user's inbox
#         results = service.users().messages().list(userId='me').execute()
#         messages = results.get('messages', [])

#         email_subjects = []
#         if not messages:
#             email_subjects.append('No messages found.')
#         else:
#             for message in messages:
#                 msg = service.users().messages().get(userId='me', id=message['id']).execute()
#                 email_subjects.append(msg.get('snippet', 'No snippet available'))

#         return email_subjects

#     except Exception as e:
#         return [f"An error occurred: {e}"]


