import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Get the client secrets from the environment variable
CLIENT_SECRETS_JSON = os.getenv('GOOGLE_CLIENT_SECRETS')

if CLIENT_SECRETS_JSON is None:
    print('Error: GOOGLE_CLIENT_SECRETS environment variable not set.')
    exit(1)

# Parse the JSON content
CLIENT_SECRETS = json.loads(CLIENT_SECRETS_JSON)

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def generate_token():
    # Create an OAuth 2.0 flow object
    flow = InstalledAppFlow.from_client_config(CLIENT_SECRETS, SCOPES)

    # Run the local server to handle the OAuth callback
    creds = flow.run_local_server(port=8080, open_browser=True)  # Ensure the port matches

    # Save the credentials to a file
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    print('Token has been saved to token.json.')

if __name__ == '__main__':
    generate_token()

