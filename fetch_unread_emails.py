import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Hardcoded values
GOOGLE_CREDENTIALS_JSON = {
    "web": {
        "client_id": "554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com",
        "project_id": "johnsite-433520",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost:9000/oauth/callback"]
    }
}

GOOGLE_REDIRECT_URI = 'http://localhost:9000/oauth/callback'
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_credentials():
    """Fetch credentials using OAuth 2.0."""
    try:
        # Create flow instance with client secrets and scopes
        flow = InstalledAppFlow.from_client_config(
            GOOGLE_CREDENTIALS_JSON,
            SCOPES
        )
        
        # Set redirect URI
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        # Get the authorization URL and ask user to visit it
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        print(f"Please go to this URL: {auth_url}")

        # The user will get a code after granting access
        code = input("Enter the authorization code: ")
        flow.fetch_token(code=code)

        # Save credentials for future use
        credentials = flow.credentials
        return credentials

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def list_unread_emails(credentials):
    """Fetch and list unread emails."""
    try:
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])

        if not messages:
            print('No unread messages.')
        else:
            print(f'Found {len(messages)} unread messages.')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(f"Snippet: {msg['snippet']}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    creds = get_credentials()
    if creds:
        list_unread_emails(creds)

