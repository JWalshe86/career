from google_auth_oauthlib.flow import InstalledAppFlow
import webbrowser

# Configuration
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

def get_authorization_url():
    # Initialize the flow using the client secrets file and scopes
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )

    # Run the local server on port 9000 and get the authorization URL
    credentials = flow.run_local_server(port=9001)

    # Print the credentials (just to confirm everything works)
    print('Credentials:', credentials)

def main():
    get_authorization_url()

if __name__ == '__main__':
    main()

