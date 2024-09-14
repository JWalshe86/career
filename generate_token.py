import os
import requests
from google_auth_oauthlib.flow import Flow

# Define the path to your client secrets file and the scopes
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def generate_token():
    # Create an OAuth 2.0 flow object
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')  # Use Heroku environment variable
    )

    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    print('Authorization URL:', authorization_url)

    # Instruct user to visit the URL and authorize the app
    print('Please visit this URL and authorize the app.')
    print('After authorization, you will be redirected to a URL with a code parameter.')
    print('Please copy that code and enter it below.')

    # Handle the redirect URI callback to get the authorization code
    code = input('Enter the authorization code: ')

    # Exchange the authorization code for tokens
    flow.fetch_token(code=code)

    # Save the credentials to a file
    credentials = flow.credentials
    with open('token.json', 'w') as token_file:
        token_file.write(credentials.to_json())

    print('Token has been saved to token.json.')

if __name__ == '__main__':
    generate_token()

