import os
import json
import logging
from django.http import HttpResponseRedirect
from django.contrib import messages  # Add this import
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from tasks.models import Task
from jobs.models import Jobsearch
from tasks.forms import TaskForm
from emails.views import get_unread_emails
from google.auth.transport.requests import Request
from django.shortcuts import render, redirect
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

def error_view(request):
    """Render error page."""
    return render(request, 'dashboard/error.html', status=500)


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)

import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.shortcuts import render, redirect
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    try:
        # Load credentials directly from token.json
        token_file = 'token.json'
        
        if not os.path.exists(token_file):
            logger.error("Token file not found.")
            return redirect('dashboard:error_view')

        with open(token_file, 'r') as file:
            token_data = json.load(file)

        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET

        if 'access_token' not in token_data or not client_id or not client_secret:
            logger.error("Missing fields in token data.")
            return redirect('dashboard:error_view')

        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )

        logger.debug(f"Loaded credentials: {creds}")

        # Refresh credentials if expired
        if creds.expired and creds.refresh_token:
            logger.debug("Credentials expired, attempting refresh.")
            creds.refresh(Request())
            logger.debug("Credentials refreshed successfully.")

        # Log type of credentials before calling get_unread_emails
        logger.debug(f"Dashboard view: creds being passed to get_unread_emails {type(creds)}")

        # Fetch unread emails and pass verified creds object
        unread_emails, error = get_unread_emails(creds)
        if error:
            logger.error(f"Error fetching unread emails: {error}")
            return redirect('dashboard:error_view')

        # Log the number of unread emails instead of the full list
        logger.debug(f"Number of unread emails retrieved: {len(unread_emails)}")

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

