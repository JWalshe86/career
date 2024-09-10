import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import logging

# Setup logging
logger = logging.getLogger(__name__)

def load_credentials():
    """
    Load OAuth2 credentials from environment variables or a file.
    
    Returns:
        Credentials: The loaded credentials.
    """
    try:
        if os.getenv('HEROKU'):
            token_json_content = os.getenv('TOKEN_JSON_CONTENT')
            if token_json_content:
                credentials_data = json.loads(token_json_content)
            else:
                raise ValueError("TOKEN_JSON_CONTENT environment variable is not set.")
        else:
            token_json_path = os.getenv('TOKEN_JSON_PATH', 'token.json')
            with open(token_json_path, 'r') as token_file:
                credentials_data = json.load(token_file)

        creds = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )
        return creds
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

def refresh_token():
    """
    Refresh OAuth2 token.
    """
    try:
        creds = load_credentials()
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token refreshed successfully.")
            print(f"New access token: {creds.token}")
        else:
            print("Token is not expired or refresh token is not available.")
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    refresh_token()

