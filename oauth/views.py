import os
import urllib.parse
import logging
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from .oauth_utils import get_unread_emails

logger = logging.getLogger(__name__)

# Print SCOPES for debugging (remove or replace with proper logging in production)
logger.debug("SCOPES in views.py: %s", settings.SCOPES)

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os
import logging

logger = logging.getLogger(__name__)

# Path to store the token
TOKEN_FILE_PATH = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def load_credentials():
    """Load credentials from the token file."""
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, 'r') as token_file:
            token_info = json.load(token_file)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            return creds
    return None

def save_credentials(creds):
    """Save credentials to the token file."""
    with open(TOKEN_FILE_PATH, 'w') as token_file:
        token_file.write(creds.to_json())
    logger.info("Credentials saved to token.json.")

def refresh_tokens(creds):
    """Refresh OAuth2 tokens."""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
            logger.info("Credentials refreshed and saved.")
        return creds
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return None

def exchange_code_for_tokens(auth_code):
    """Exchange the authorization code for tokens."""
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': auth_code,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
            'grant_type': 'authorization_code'
        }
    )
    tokens = response.json()
    if 'error' in tokens:
        logger.error(f"Error exchanging code for tokens: {tokens.get('error_description', 'No error description')}")
        raise Exception("Error exchanging code for tokens")
    
    creds = Credentials.from_authorized_user_info(tokens, SCOPES)
    save_credentials(creds)
    return creds

def get_oauth2_authorization_url():
    """Generate OAuth2 authorization URL."""
    logger.debug("Generating OAuth2 authorization URL.")
    try:
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        credentials_data = json.loads(google_credentials_json)

        if 'web' not in credentials_data:
            logger.error(f"Invalid client secrets format: {credentials_data}")
            raise ValueError("Invalid client secrets format. Must contain 'web'.")

        flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

def get_unread_emails(auth_code=None):
    """Fetch unread emails from Gmail."""
    creds = None
    auth_url = None

    if auth_code:
        try:
            creds = exchange_code_for_tokens(auth_code)
        except Exception as e:
            logger.error(f"Error handling authorization code: {e}")
            return [], None

    if creds:
        creds = refresh_tokens(creds)
        if not creds:
            auth_url = get_oauth2_authorization_url()
            return [], auth_url
    else:
        creds = load_credentials()
        if creds:
            creds = refresh_tokens(creds)
            if not creds:
                auth_url = get_oauth2_authorization_url()
                return [], auth_url
        else:
            logger.debug("No valid credentials found. Redirecting to authorization URL.")
            auth_url = get_oauth2_authorization_url()
            return [], auth_url

    try:
        service = build("gmail", "v1", credentials=creds)
        excluded_senders = [
            "no-reply@usebubbles.com",
            "chandeep@2toucans.com",
            "craig@itcareerswitch.co.uk",
            "no-reply@swagapp.com",
            "no-reply@fathom.video",
            "mailer@jobleads.com",
            "careerservice@email.jobleads.com"
        ]
        query = "is:unread -category:social -category:promotions"
        for sender in excluded_senders:
            query += f" -from:{sender}"
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get('messages', [])

        unread_emails = []
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            snippet = msg['snippet']
            email_data = {
                'id': message['id'],
                'snippet': snippet,
                'sender': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'),
                'subject': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'),
                'highlight': 'highlight' if 'unfortunately' in snippet.lower() else ''
            }
            unread_emails.append(email_data)

        logger.info(f"Processed unread emails: {unread_emails}")
        return unread_emails, None
    except Exception as e:
        logger.error(f"An error occurred while fetching emails: {e}")
        return [], None




def jobs_dashboard_with_emails_or_callback(request):
    if 'code' in request.GET:
        code = request.GET.get('code')
        logger.debug(f"Authorization code received: {code}")

        if not code:
            logger.error("No authorization code provided.")
            return HttpResponse("Authorization code missing.", status=400)

        try:
            client_config = {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "project_id": "johnsite-433520",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                }
            }
            
            # Create the OAuth2 flow object
            logger.debug("Creating OAuth2 flow object.")
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=settings.SCOPES
            )
            
            # Fetch the token using the provided code
            logger.debug("Fetching token with the authorization code.")
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Save the credentials to a file
            logger.debug("Saving credentials to 'token.json'.")
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
                
            logger.info("OAuth2 authorization completed successfully.")
            return redirect('jobs_dashboard_with_emails')
        except GoogleAuthError as e:
            logger.error(f"OAuth2 error: {e}")
            return HttpResponse("OAuth2 error occurred.", status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return HttpResponse("An unexpected error occurred.", status=500)
    else:
        logger.debug("No authorization code present in request.")
        logger.debug("Rendering jobs dashboard with emails.")

        try:
            email_subjects, auth_url = get_unread_emails()
            logger.debug(f"Email subjects: {email_subjects}")
            
            if auth_url:
                logger.debug(f"Redirecting to authorization URL: {auth_url}")
                return redirect(auth_url)

            unread_email_count = len(email_subjects) if email_subjects else 0
            context = {
                'email_subjects': email_subjects,
                'unread_email_count': unread_email_count,
            }
            return render(request, "jobs/jobs_dashboard.html", context)
        except Exception as e:
            logger.error(f"Error in getting unread emails or rendering dashboard: {e}")
            return HttpResponse("An unexpected error occurred while fetching emails.", status=500)

def generate_authorization_url(client_id, scopes, state):
    logger.debug('Generating authorization URL')
    flow = InstalledAppFlow.from_client_config(
        settings.GOOGLE_CREDENTIALS,
        scopes
    )
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        state=state
    )
    logger.debug(f'Authorization URL: {authorization_url}')  # Log the full URL
    return authorization_url


from google_auth_oauthlib.flow import Flow

# Setup logging
logger = logging.getLogger(__name__)

def oauth_login(request):
    # Debugging output
    logger.debug("Starting OAuth login process")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": "johnsite-433520",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": ["https://www.jwalshedev.ie/oauth/jobs-dashboard/"]  # Hardcoded redirect URI
        }
    }

    redirect_uri = "https://www.jwalshedev.ie/oauth/jobs-dashboard/"  # Hardcoded redirect URI

    # Debugging output
    logger.debug(f"Client config: {client_config}")
    logger.debug(f"Redirect URI: {redirect_uri}")

    try:
        # Create the OAuth Flow object
        flow = Flow.from_client_config(
            client_config,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            redirect_uri=redirect_uri
        )
        
        # Debugging output
        logger.debug("OAuth Flow object created successfully")
        
        # Generate the authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Debugging output
        logger.debug(f"Authorization URL: {authorization_url}")
        logger.debug(f"State: {state}")
        
        # Redirect to the authorization URL
        return redirect(authorization_url)
    
    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"Error during OAuth login process: {e}")
        return redirect('/')  # Redirect to home or error page




def env_vars(request):
    env_vars = {
        'DEBUG': os.getenv('DEBUG'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI'),
    }
    return JsonResponse(env_vars)

