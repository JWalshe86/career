import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

GOOGLE_CREDENTIALS_JSON = {
    "web": {
        "client_id": "554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com",
        "project_id": "johnsite-433520",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["https://www.jwalshedev.ie:9000/oauth/callback/"]
    }
}

GOOGLE_REDIRECT_URI = 'http://www.jwalshedev.ie/oauth/callback/'
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_credentials():
    try:
        flow = InstalledAppFlow.from_client_config(
            GOOGLE_CREDENTIALS_JSON,
            SCOPES
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        print(f"Please go to this URL and authorize the app: {auth_url}")
        
        code = input("Enter the authorization code: ")
        flow.fetch_token(code=code)

        credentials = flow.credentials
        return credentials

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == '__main__':
    creds = get_credentials()

