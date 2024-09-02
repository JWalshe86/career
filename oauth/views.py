# oauth/views.py
from django.shortcuts import render, redirect
from django.conf import settings
from .oauth_utils import get_oauth2_authorization_url, get_unread_emails
import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.shortcuts import redirect
from google_auth_oauthlib.flow import InstalledAppFlow

def oauth2callback(request):
    code = request.GET.get('code')
    if not code:
        logger.error("No authorization code provided.")
        return HttpResponse("Authorization code missing.", status=400)
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        logger.info("OAuth2 authorization completed successfully.")
        return redirect('dashboard')  # Redirect to the dashboard or another page
    except (GoogleAuthError, InsecureTransportError) as e:
        logger.error(f"OAuth2 error: {e}")
        return HttpResponse("OAuth2 error occurred.", status=500)


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

