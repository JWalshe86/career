import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load credentials from token.json
with open('token.json', 'r') as token_file:
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
results = service.users().messages().list(userId='me').execute()
messages = results.get('messages', [])

if not messages:
    print('No messages found.')
else:
    print('Messages:')
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print(f"Message snippet: {msg['snippet']}")

