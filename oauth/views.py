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
from .oauth_utils import load_credentials_from_db, save_credentials_to_db, get_unread_emails
from emails.views import get_unread_emails
from oauthlib.oauth2 import WebApplicationClient

# Setup logging
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def jobs_dashboard_with_emails_or_callback(request):
    """
    Handle the jobs dashboard view with or without OAuth2 callback.
    """
    if not request.user.is_authenticated:
        return HttpResponse("User must be logged in to access this page.", status=403)

    try:
        # Fetch unread emails with the user argument
        email_subjects, auth_url = get_unread_emails(request.user)
        if auth_url:
            # If there's an auth URL, it means credentials need to be refreshed
            return redirect(auth_url)

        unread_email_count = len(email_subjects) if email_subjects else 0
        context = {
            'email_subjects': email_subjects,
            'unread_email_count': unread_email_count,
        }
        # Render the dashboard with the email context
        return render(request, "dashboard/dashboard.html", context)
    except Exception as e:
        logger.error(f"Error in getting unread emails or rendering dashboard: {e}")
        return HttpResponse("An unexpected error occurred while fetching emails.", status=500)


def refresh_tokens(user, creds):
    """
    Refresh OAuth2 tokens if they are expired.
    
    Args:
        user (User): The Django user whose credentials are being refreshed.
        creds (Credentials): The credentials to refresh.
    
    Returns:
        Credentials: Refreshed credentials or None if refresh failed.
    """
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials to the database
            save_credentials_to_db(user, creds)
            logger.info("Credentials refreshed and saved.")
        return creds
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return None


import requests

def exchange_code_for_tokens(auth_code):
    """
    Exchange the authorization code for tokens.
    
    Args:
        auth_code (str): The authorization code received from the OAuth2 flow.
    
    Returns:
        dict: Tokens obtained from the exchange.
    
    Raises:
        Exception: If there is an error exchanging the code for tokens.
    """
    try:
        redirect_uri = 'https://4f81-84-203-41-130.ngrok-free.app/oauth/jobs-dashboard/'
        client_id = '554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com'
        client_secret = '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'
        
        # Log details of the request for debugging
        print(f"Using Redirect URI: {redirect_uri}")
        print(f"Authorization Code: {auth_code}")
        print(f"Client ID: {client_id}")

        # Request tokens from Google
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': auth_code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )

        # Log response for debugging
        print(f"Token exchange response: {response.status_code} - {response.text}")

        if response.status_code != 200:
            tokens = response.json()
            if 'error' in tokens:
                error = tokens.get('error')
                error_description = tokens.get('error_description', 'No error description')
                print(f"Error in token response: {error} - {error_description}")
                
                if error == 'invalid_grant':
                    print("The authorization code may be invalid or expired.")
                raise Exception("Error exchanging code for tokens")
        
        return response.json()

    except requests.RequestException as req_err:
        print(f"Request error during token exchange: {req_err}")
        raise
    except Exception as e:
        print(f"Error during token exchange: {e}")
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
        # Load Google credentials from environment variable
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        credentials_data = json.loads(google_credentials_json)

        if 'web' not in credentials_data:
            logger.error(f"Invalid client secrets format: {credentials_data}")
            raise ValueError("Invalid client secrets format. Must contain 'web'.")

        # Initialize the OAuth2 client
        client_id = credentials_data['web']['client_id']
        authorization_endpoint = "https://accounts.google.com/o/oauth2/auth"

        client = WebApplicationClient(client_id)

        # Hardcoded redirect URI for local development
        redirect_uri = 'http://localhost:9000/oauth/jobs-dashboard/'

        # Construct the authorization URL
        authorization_url = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,  # Hardcoded local redirect URI
            scope=SCOPES,
            access_type='offline',
            include_granted_scopes='true'
        )
        
        logger.info(f"Generated authorization URL: {authorization_url}")
        return authorization_url

    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise



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
            "redirect_uris": ["https://localhost:9000/oauth/jobs-dashboard/"]
        }
    }

    redirect_uri = "https://localhost:9000/oauth/jobs-dashboard/"

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


import requests

def check_auth_code_validity(auth_code):
    """
    Check the validity of an authorization code by attempting to exchange it for tokens.
    
    Args:
        auth_code (str): The authorization code to check.
    
    Returns:
        dict: The response from the token exchange request.
    
    Raises:
        Exception: If the code is invalid or expired.
    """
    try:
        redirect_uri = 'https://4f81-84-203-41-130.ngrok-free.app/oauth/jobs-dashboard/'
        client_id = '554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com'
        client_secret = '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'
        
        # Print the authorization code for debugging
        print(f"Authorization Code: {auth_code}")

        # Request tokens from Google
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': auth_code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )

        # Print response for debugging
        print(f"Token exchange response: {response.status_code} - {response.text}")

        if response.status_code != 200:
            tokens = response.json()
            if 'error' in tokens:
                error = tokens.get('error')
                error_description = tokens.get('error_description', 'No error description')
                print(f"Error in token response: {error} - {error_description}")
                if error == 'invalid_grant':
                    print("The authorization code may be invalid or expired.")
                elif error == 'redirect_uri_mismatch':
                    print("The redirect URI does not match what is registered in the Google API Console.")
                raise Exception("Error exchanging code for tokens")
        
        return response.json()

    except requests.RequestException as req_err:
        print(f"Request error during token exchange: {req_err}")
        raise
    except Exception as e:
        print(f"Error during token exchange: {e}")
        raise

