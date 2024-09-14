from django.core.management.base import BaseCommand
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class Command(BaseCommand):
    help = 'Fetch unread emails from Gmail'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching unread emails...')
        try:
            fetch_unread_emails()
        except Exception as e:
            self.stderr.write(f'Error: {e}')

def fetch_unread_emails():
    token_json_content = os.getenv('TOKEN_JSON_CONTENT')
    if not token_json_content:
        raise ValueError("TOKEN_JSON_CONTENT environment variable is not set.")

    token_data = json.loads(token_json_content)
    credentials = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )

    service = build('gmail', 'v1', credentials=credentials)
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No unread messages found.')
    else:
        print('Unread messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg['snippet']
            print(f'- {snippet}')

