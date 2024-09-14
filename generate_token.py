import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the path to your client secrets file and the scopes
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Check if the credentials file exists
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f'Error: {CLIENT_SECRETS_FILE} file not found.')
        return

    # Create an OAuth 2.0 flow object
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

    # Run the local server to handle the OAuth callback
    creds = flow.run_local_server(port=8080, open_browser=True)  # Ensure the port matches

    # Save the credentials to a file
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    print('Token has been saved to token.json.')

if __name__ == '__main__':
    main()

