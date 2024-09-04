import os
import json
import logging
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .oauth_utils import get_unread_emails

# Setup logging
logger = logging.getLogger(__name__)

# Path to store the token file and scopes for Gmail API
TOKEN_FILE_PATH = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def load_credentials():
    """
    Load credentials from the token file.
    
    Returns:
        Credentials: Loaded credentials if file exists, otherwise None.
    """
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, 'r') as token_file:
            token_info = json.load(token_file)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            return creds
    return None

def save_credentials(creds):
    """
    Save credentials to the token file.
    
    Args:
        creds (Credentials): The credentials to save.
    """
    with open(TOKEN_FILE_PATH, 'w') as token_file:
        token_file.write(creds.to_json())
    logger.info("Credentials saved to token.json.")

def refresh_tokens(creds):
    """
    Refresh OAuth2 tokens if they are expired.
    
    Args:
        creds (Credentials): The credentials to refresh.
    
    Returns:
        Credentials: Refreshed credentials or None if refresh failed.
    """
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
    """
    Exchange the authorization code for tokens.
    
    Args:
        auth_code (str): The authorization code received from the OAuth2 flow.
    
    Returns:
        Credentials: Credentials object with the obtained tokens.
    
    Raises:
        Exception: If there is an error exchanging the code for tokens.
    """
    try:
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
    except Exception as e:
        # ** RED FLAG: Error handling authorization code exchange **
        logger.error(f"Error during token exchange: {e}")
        raise

def get_oauth2_authorization_url():
    """
    Generate OAuth2 authorization URL.
    
    Returns:
        str: The authorization URL for OAuth2 login.
    
    Raises:
        Exception: If there is an error generating the authorization URL.
    """
    logger.debug("Generating OAuth2 authorization URL.")
    try:
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        credentials_data = json.loads(google_credentials_json)

        if 'web' not in credentials_data:
            logger.error(f"Invalid client secrets format: {credentials_data}")
            raise ValueError("Invalid client secrets format. Must contain 'web'.")

        flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            redirect_uri='https://www.jwalshedev.ie/oauth/jobs-dashboard/'  # Ensure this is registered in the Google Cloud Console
        )
        logger.info(f"Generated authorization URL: {authorization_url}")
        return authorization_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

def get_unread_emails(auth_code=None):
    """
    Fetch unread emails from Gmail.
    
    Args:
        auth_code (str, optional): The authorization code received from the OAuth2 flow.
    
    Returns:
        tuple: A tuple containing a list of unread emails and an authorization URL if needed.
    """
    creds = None
    auth_url = None

    if auth_code:
        try:
            creds = exchange_code_for_tokens(auth_code)
        except Exception as e:
            # ** RED FLAG: Error handling authorization code **
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
        # ** RED FLAG: Error fetching unread emails **
        logger.error(f"An error occurred while fetching emails: {e}")
        return [], None

def oauth_login(request):
    """
    Handle OAuth2 login by redirecting to the authorization URL.
    
    Args:
        request (HttpRequest): The incoming HTTP request.
    
    Returns:
        HttpResponse: Redirect response to the authorization URL or home on error.
    """
    logger.debug("Starting OAuth login process")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": "johnsite-433520",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": ["https://www.jwalshedev.ie/oauth/jobs-dashboard/"]
        }
    }

    redirect_uri = "https://www.jwalshedev.ie/oauth/jobs-dashboard/"

    logger.debug(f"Client config: {client_config}")
    logger.debug(f"Redirect URI: {redirect_uri}")

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            redirect_uri=redirect_uri
        )

        logger.debug("OAuth Flow object created successfully")

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        logger.debug(f"Authorization URL: {authorization_url}")
        logger.debug(f"State: {state}")

        return redirect(authorization_url)
    except Exception as e:
        # ** RED FLAG: Error during OAuth login process **
        logger.error(f"Error during OAuth login process: {e}")
        return redirect('/')  # Redirect to home or error page

def jobs_dashboard_with_emails_or_callback(request):
    """
    Handle the jobs dashboard view or OAuth2 callback.
    
    Args:
        request (HttpRequest): The incoming HTTP request.
    
    Returns:
        HttpResponse: The jobs dashboard page or redirect to authorization URL.
    """
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

            logger.debug("Creating OAuth2 flow object.")
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=settings.SCOPES
            )

            logger.debug("Fetching token with the authorization code.")
            flow.fetch_token(code=code)
            creds = flow.credentials

            logger.debug("Saving credentials to 'token.json'.")
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())

            logger.info("OAuth2 authorization completed successfully.")
            return redirect('jobs_dashboard_with_emails')
        except GoogleAuthError as e:
            # ** RED FLAG: OAuth2 error during callback handling **
            logger.error(f"OAuth2 error: {e}")
            return HttpResponse("OAuth2 error occurred.", status=500)
        except Exception as e:
            # ** RED FLAG: Unexpected error during callback handling **
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
            # ** RED FLAG: Error rendering dashboard or getting emails **
            logger.error(f"Error in getting unread emails or rendering dashboard: {e}")
            return HttpResponse("An unexpected error occurred while fetching emails.", status=500)

def env_vars(request):
    """
    Return environment variables as JSON response.
    
    Args:
        request (HttpRequest): The incoming HTTP request.
    
    Returns:
        JsonResponse: JSON response containing environment variables.
    """
    env_vars = {
        'DEBUG': os.getenv('DEBUG'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI'),
    }
    return JsonResponse(env_vars)

