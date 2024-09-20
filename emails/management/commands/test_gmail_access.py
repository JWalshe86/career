# myapp/management/commands/test_gmail_access.py
import os
import json
from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class Command(BaseCommand):
    help = 'Test access to Gmail data using OAuth2 credentials'

    def handle(self, *args, **kwargs):
        try:
            # Load the credentials from the file
            with open('token.json', 'r') as token_file:
                creds = Credentials.from_authorized_user_file('token.json')

            # Create a Gmail API service instance
            service = build('gmail', 'v1', credentials=creds)

            # Fetch the list of labels
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                self.stdout.write('No labels found.')
            else:
                self.stdout.write('Labels:')
                for label in labels:
                    self.stdout.write(f"- {label['name']}")

        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")

