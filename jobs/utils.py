import os
import logging
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_oauth2_authorization_url():
    logger.debug("Starting to generate OAuth2 authorization URL.")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        logger.info("Generated authorization URL: %s", auth_url)
        return auth_url
    except Exception as e:
        logger.error("Error generating authorization URL: %s", e)
        raise

def get_unread_emails():
    creds = None
    # Load credentials from file
    if os.path.exists(settings.TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(settings.TOKEN_FILE_PATH, SCOPES)

    if not creds or not creds.valid:
        # Handle invalid credentials
        return [], get_oauth2_authorization_url()

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        email_subjects = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_subjects.append({
                'subject': msg['payload']['headers'][0]['value'],
                'sender': msg['payload']['headers'][1]['value'],
                'snippet': msg['snippet']
            })
        return email_subjects, None
    except Exception as e:
        logger.error("Error retrieving unread emails: %s", e)
        return [], None
