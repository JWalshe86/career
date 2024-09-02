# oauth/views.py

from django.shortcuts import render, redirect
from django.conf import settings
from .oauth_utils import get_oauth2_authorization_url, get_unread_emails
from google.auth.exceptions import GoogleAuthError
from oauthlib.oauth2 import InsecureTransportError
import logging

logger = logging.getLogger(__name__)

def oauth2callback(request):
    # Implementation for handling the OAuth2 callback
    pass

def jobs_dashboard_with_emails(request):
    logger.debug("Rendering jobs dashboard with emails.")
    email_subjects, auth_url = get_unread_emails()
    if auth_url:
        logger.debug(f"Redirecting to authorization URL: {auth_url}")
        return redirect(auth_url)

    unread_email_count = len(email_subjects) if email_subjects else 0
    context = {
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
        # Add other context data as needed
    }
    return render(request, "jobs/jobs_dashboard.html", context)

