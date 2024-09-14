import os
import json
import logging
import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .oauth_utils import load_credentials_from_db, save_credentials_to_db, get_unread_emails, refresh_tokens
from emails.views import get_unread_emails
from oauthlib.oauth2 import WebApplicationClient

# Setup logging
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }

    redirect_uri = settings.GOOGLE_REDIRECT_URI

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


def oauth_callback(request):
    """
    Handle the OAuth2 callback from Google and exchange the authorization code for an access token.
    """
    logger.info("OAuth callback view accessed")
    
    code = request.GET.get('code')
    if not code:
        logger.error("Authorization code missing")
        return HttpResponse('Authorization code missing.', status=400)

    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    logger.info("Redirect URI used: %s", redirect_uri)
    
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    response_data = response.json()
    
    logger.info("OAuth token response: %s", response_data)
    
    if 'access_token' not in response_data:
        logger.error("Failed to get access token: %s", response_data)
        return HttpResponse('Failed to get access token.', status=400)

    # Store the access token in the session
    request.session['access_token'] = response_data['access_token']
    request.session['refresh_token'] = response_data.get('refresh_token')  # Store refresh token if available
    
    # Redirect to the dashboard
    return redirect('/')



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
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        
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
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET

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

