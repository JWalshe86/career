import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
from google_auth_oauthlib.flow import InstalledAppFlow

# Load the client secrets file
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

# Get the authorization URL
auth_url, _ = flow.authorization_url(access_type='offline')
print('Please go to this URL and authorize the application:', auth_url)

# Get the authorization code from the user
auth_code = input('Enter the authorization code: ')

# Exchange the authorization code for tokens
flow.fetch_token(code=auth_code)

# Save the credentials
credentials = flow.credentials
print('Access token:', credentials.token)
print('Refresh token:', credentials.refresh_token)

def get_credentials():
    try:
        # Load the token JSON from environment variable
        token_json = json.loads(os.getenv('GMAIL_TOKEN_JSON', '{}'))
        access_token = token_json.get('access_token')
        refresh_token = token_json.get('refresh_token')
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not access_token or not refresh_token or not client_id or not client_secret:
            raise ValueError("Missing required credentials.")

        return access_token, refresh_token, client_id, client_secret
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in GMAIL_TOKEN_JSON.")

def refresh_access_token():
    access_token, refresh_token, client_id, client_secret = get_credentials()

    # Token endpoint for Google's OAuth2
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    # Parameters for the POST request
    data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    
    response = requests.post(token_endpoint, data=data)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('access_token')
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    new_access_token = refresh_access_token()
    if new_access_token:
        print(f"New access token: {new_access_token}")
    else:
        print("Failed to refresh access token.")

