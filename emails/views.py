import logging
from django.http import HttpResponse
from django.shortcuts import render
from .utils import get_unread_emails, refresh_credentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from django.shortcuts import render, redirect
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging

# Configure logging
logger = logging.getLogger(__name__)

def display_emails(request):
    """Render the section of the main dashboard showing unread emails."""
    logger.debug("Rendering display emails section.")

    if not request.user.is_authenticated:
        return HttpResponse("User must be logged in to access this page.", status=403)

    try:
        # Load credentials and debug
        creds = load_credentials()  # This should return a google.oauth2.credentials.Credentials object
        logger.debug(f"Loaded credentials: {creds}")

        if not creds:
            logger.error("No credentials found.")
            return redirect('dashboard:error_view')

        # Check if credentials are expired and refresh if necessary
        if creds.expired and creds.refresh_token:
            logger.debug("Credentials expired, attempting refresh.")
            creds.refresh(Request())
            logger.debug("Credentials refreshed successfully.")

        # Ensure `creds` is a `Credentials` object
        if not isinstance(creds, Credentials):
            raise TypeError("Credentials object is not of the correct type")
        
        logger.debug(f"Credentials type: {type(creds)}")
        
        # Fetch unread emails
        unread_emails, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error fetching unread emails: {error}")
            return redirect('dashboard:error_view')

        logger.debug(f"Unread emails retrieved: {unread_emails}")

        # Render the template with unread emails
        context = {
            'email_subjects': unread_emails,
            'unread_email_count': len(unread_emails) if unread_emails else 0,
        }
        return render(request, "emails/display_emails.html", context)

    except Exception as e:
        logger.error(f"Unexpected error in display_emails view: {e}", exc_info=True)
        return redirect('dashboard:error_view')

