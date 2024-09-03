import os
import urllib.parse
import logging
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from .oauth_utils import get_unread_emails

logger = logging.getLogger(__name__)

# Print SCOPES for debugging (remove or replace with proper logging in production)
logger.debug("SCOPES in views.py: %s", settings.SCOPES)


def jobs_dashboard_with_emails_or_callback(request):
    if 'code' in request.GET:
        code = request.GET.get('code')
        logger.debug(f"Authorization code received: {code}")
        if not code:
            logger.error("No authorization code provided.")
            return HttpResponse("Authorization code missing.", status=400)

        try:
            flow = InstalledAppFlow.from_client_config(
                settings.GOOGLE_CREDENTIALS,
                settings.SCOPES
            )
            flow.fetch_token(code=code)
            creds = flow.credentials
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
        logger.debug("Rendering jobs dashboard with emails.")
        email_subjects, auth_url = get_unread_emails()
        if auth_url:
            logger.debug(f"Redirecting to authorization URL: {auth_url}")
            return redirect(auth_url)

        unread_email_count = len(email_subjects) if email_subjects else 0
        context = {
            'email_subjects': email_subjects,
            'unread_email_count': unread_email_count,
        }
        return render(request, "jobs/jobs_dashboard.html", context)


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


from django.shortcuts import redirect
from google_auth_oauthlib.flow import InstalledAppFlow
from django.http import HttpResponse

from django.shortcuts import redirect
from google_auth_oauthlib.flow import InstalledAppFlow
from django.http import HttpResponse



# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def oauth_login(request):
    # Configuration with your client secret and client ID
    client_config = {
        "web": {
            "client_id": "554722957427-8i5p5m7jd1vobctsb34ql0km1qorpihg.apps.googleusercontent.com",
            "project_id": "johnsite-433520",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": [
                "http://localhost:8000/oauth/jobs-dashboard/",
                "https://www.jwalshedev.ie/oauth/jobs-dashboard/",
                "https://johnsite-d251709cf12b.herokuapp.com/jobs-dashboard/oauth2callback/"
            ]
        }
    }

    # Create a Flow instance with your configuration
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        redirect_uri="http://localhost:8000/oauth/jobs-dashboard/"  # Use appropriate redirect URI based on the environment
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    logger.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

def env_vars(request):
    env_vars = {
        'DEBUG': os.getenv('DEBUG'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI'),
    }
    return JsonResponse(env_vars)

def exchange_code_for_tokens(auth_code):
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': auth_code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        response.raise_for_status()  # Ensure we raise an error for bad HTTP responses
        tokens = response.json()
        return tokens
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging code for tokens: {e}")
        raise

