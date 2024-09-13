import os
import json
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from tasks.models import Task
from jobs.models import Jobsearch
from django.http import HttpResponse
from emails.views import get_unread_emails, load_credentials, create_credentials, refresh_credentials
from google.auth.exceptions import GoogleAuthError, RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from tasks.forms import TaskForm

logger = logging.getLogger(__name__)


def dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponse("User must be logged in to access this page.", status=403)

    try:
        # Load credentials
        credentials_data = load_credentials()
        creds = create_credentials(credentials_data)

        # Refresh the credentials if needed
        if creds and creds.expired and creds.refresh_token:
            creds = refresh_credentials(creds)
        elif creds.expired and not creds.refresh_token:
            logger.warning("Token expired and no refresh token available. Redirecting to OAuth login.")
            return redirect(reverse('oauth:oauth_login'))

        # Fetch unread emails
        unread_emails, auth_url = get_unread_emails(creds)

        if auth_url:
            return redirect(auth_url)

        # Render dashboard with unread emails
        context = {
            'unread_emails': unread_emails,
            'unread_email_count': len(unread_emails),
        }
        return render(request, "dashboard/dashboard.html", context)

    except RefreshError as refresh_error:
        logger.error(f"Google token refresh error: {refresh_error}")
        logger.debug("Redirecting to OAuth login due to token refresh error.")
        return redirect(reverse('oauth:oauth_login'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug("Returning 500 response due to unexpected error.")
        return HttpResponse("An unexpected error occurred. Please try again.", status=500)



def dashboard_searched(request):
    """Render dashboard with searched jobs."""
    logger.debug("Rendering dashboard with searched jobs.")

    today = timezone.now().date()
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info("Task form submitted and saved.")
            return redirect(reverse('dashboard_searched'))

    time_periods = {
        "one_week_ago": today - timedelta(days=7),
        "two_weeks_ago": today - timedelta(days=14),
        "one_month_ago": today - timedelta(days=30),
    }

    status_updates = [
        ({"created_at__gt": time_periods["one_week_ago"], "job_status": "contacted"}, "week"),
        ({"created_at__gt": time_periods["two_weeks_ago"], "job_status": "contacted"}, "two_weeks"),
        ({"created_at__gt": time_periods["one_month_ago"], "job_status": "contacted"}, "month"),
    ]

    context = {
        "tasks": tasks,
        "form": form,
        "time_periods": time_periods,
    }

    for filters, period in status_updates:
        jobs = Jobsearch.objects.filter(**filters).annotate(
            contacted=Count('job_status', filter=Q(job_status='contacted'))
        ).count()
        context[f'jobs_contacted_{period}'] = jobs
        logger.debug(f"Jobs contacted in the last {period}: {jobs}")

    return render(request, "dashboard/dashboard_searched.html", context)
