from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# Replace these values with your credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REFRESH_TOKEN = 'YOUR_REFRESH_TOKEN'
TOKEN_URI = 'https://oauth2.googleapis.com/token'

def refresh_access_token(client_id, client_secret, refresh_token, token_uri):
    # Create a Credentials object with the refresh token
    credentials = Credentials(
        None,  # Access token will be set later
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Refresh the access token
    if credentials.expired:
        credentials.refresh(Request())
    
    # Print the new access token
    print(f"New access token: {credentials.token}")

if __name__ == "__main__":
    refresh_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, TOKEN_URI)

