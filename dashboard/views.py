import os
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from oauth.models import OAuthToken
from tasks.forms import TaskForm
from tasks.models import Task
from jobs.models import Jobsearch
from emails.views import get_unread_emails

# Setup logger
logger = logging.getLogger(__name__)

def error_view(request):
    """Render error page."""
    return render(request, 'dashboard/error.html', status=500)


from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.utils import timezone
import logging

# Assuming you have a logger configured
logger = logging.getLogger(__name__)


from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.utils import timezone
import logging

# Assuming you have a logger configured
logger = logging.getLogger(__name__)


from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.utils import timezone
import logging

# Logger configuration
logger = logging.getLogger(__name__)

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.utils import timezone
import logging

# Logger configuration
logger = logging.getLogger(__name__)

def get_utc_now():
    """Return the current time as an aware datetime."""
    return timezone.now()

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.utils import timezone
import logging

# Logger configuration
logger = logging.getLogger(__name__)

def get_utc_now():
    """Return the current time as an aware datetime."""
    return timezone.now()

from django.utils import timezone

def dashboard(request):
    try:
        user = request.user
        token_data = OAuthToken.objects.filter(user=user).first()

        if not token_data:
            logger.error("No token data found in the database.")
            return redirect('dashboard:error_view')

        # Ensure the expiry time is aware
        if token_data.expiry and timezone.is_naive(token_data.expiry):
            token_data.expiry = timezone.make_aware(token_data.expiry)

        creds = Credentials(
            token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            token_uri=token_data.token_uri,
            client_id=token_data.client_id,
            client_secret=token_data.client_secret,
            scopes=token_data.scopes.split(','),
        )

        # Ensure creds.expiry is aware
        if creds.expiry and timezone.is_naive(creds.expiry):
            creds.expiry = timezone.make_aware(creds.expiry)

        current_time = timezone.now()  # Ensure current time is aware

        # Check if the credentials are expired or about to expire
        if creds.expiry is None or creds.expiry < current_time:
            if creds.refresh_token:
                logger.debug("Refreshing token.")
                creds.refresh(Request())
                token_data.access_token = creds.token
                token_data.expiry = creds.expiry if creds.expiry else current_time
                token_data.save()
                logger.debug("Refreshed token saved to the database.")
            else:
                logger.error("No refresh token available; cannot refresh credentials.")
                return redirect('dashboard:error_view')

        # Fetch unread emails
        unread_emails, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error fetching unread emails: {error}")
            return redirect('dashboard:error_view')

        # Render the dashboard template with unread emails
        return render(request, 'dashboard/dashboard.html', {'unread_emails': unread_emails})

    except Exception as e:
        logger.error(f"Unexpected error in dashboard view: {e}", exc_info=True)
        return redirect('dashboard:error_view')

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

