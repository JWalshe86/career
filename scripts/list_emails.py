import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_credentials():
    # Hardcoded token.json content
    token_json_content = '''
    {
        "token": "ya29.a0AcM612yfkQCayqMYT5-DN_xDnVTjjZrRZZY5yGP6JHRVZXzQRh5MImRNCIwOlIigSLtKICq8SLOTC1nbD1VQU1Ej5O4h6e5G_XeTiZVehPsVsU80WpBk8-IHkffv1clAb09EFz7F4FpEyjOsdVxwDcB10-1yPmeVZA2hFtS3xAaCgYKAfESARESFQHGX2MixNGe9x5k1BATXkE5ht7jvg0177",
        "refresh_token": "1//09rLfVZGZF9plCgYIARAAGAkSNwF-L9IrQvgywgMQuI5zW-t8BEPNVv1_vbZNwQ9XhJ5b8HVN2Zr3Mnbix9ULtKGJcNqra5d6y6w",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com",
        "client_secret": "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",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "universe_domain": "googleapis.com",
        "expiry": "2024-09-04T22:32:59.726508Z"
    }
    '''
    
    credentials_data = json.loads(token_json_content)

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

