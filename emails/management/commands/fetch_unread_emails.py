import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Fetch unread emails'

    def handle(self, *args, **options):
        creds = self.get_credentials()
        if not creds:
            self.stderr.write("No valid credentials found.")
            return

        try:
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
            messages = results.get('messages', [])

            if not messages:
                self.stdout.write("No unread messages.")
            else:
                self.stdout.write(f"Found {len(messages)} unread messages.")
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    self.stdout.write(f"Message snippet: {msg['snippet']}")

        except HttpError as error:
            self.stderr.write(f"An error occurred: {error}")

    def get_credentials(self):
        """Fetch credentials using OAuth 2.0 or use token from environment variables."""
        try:
            token_json = os.getenv('GMAIL_TOKEN_JSON')
            if token_json:
                print("Using token from environment variable.")
                token_info = json.loads(token_json)
                credentials = Credentials(
                    token=token_info['access_token'],
                    refresh_token=token_info.get('refresh_token'),
                    token_uri=token_info.get('token_uri'),
                    client_id=os.getenv('GOOGLE_CLIENT_ID'),
                    client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
                )
            else:
                # Handle case where token is not found
                raise ValueError("No token found. Re-authentication required.")

            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except google.auth.exceptions.RefreshError:
                    print("Token is invalid. Please reauthorize.")
                    # Handle reauthorization flow
                    # ...

            return credentials

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

