import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_credentials():
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
    return creds

def list_messages():
    try:
        # Get credentials
        creds = get_credentials()

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

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_messages()

