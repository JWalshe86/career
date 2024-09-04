import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Update with your actual file path if necessary

# Scopes required to access OAuth 2.0 client details
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Cloud API client
service = build('oauth2', 'v2', credentials=credentials)

def get_redirect_uris():
    # Your actual project ID
    project_id = 'johnsite-433520'
    
    # Fetch OAuth 2.0 client details
    request = service.projects().oauth2Client().list(parent=f'projects/{project_id}')
    response = request.execute()
    
    # Print out the redirect URIs for each OAuth 2.0 client
    print("Redirect URIs:")
    for client in response.get('clients', []):
        print(f"Client ID: {client.get('clientId')}")
        redirect_uris = client.get('redirectUris', [])
        for uri in redirect_uris:
            print(f" - {uri}")

if __name__ == '__main__':
    get_redirect_uris()

