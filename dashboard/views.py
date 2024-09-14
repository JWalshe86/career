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


def error_view(request):
    return render(request, 'dashboard/error.html', status=500)


def dashboard(request):
    """Dashboard view displaying unread emails."""
    try:
        # Retrieve credentials from the session
        creds = Credentials.from_authorized_user_info(request.session.get('credentials'))
        
        # Fetch unread emails
        unread_emails, error = get_unread_emails(creds)
        
        if error:
            # Handle the error (e.g., display an error page or message)
            logger.error(f"Error in dashboard view: {error}")
            return HttpResponseRedirect(reverse('dashboard:error_view'))
        
        # Render the dashboard with unread emails
        context = {'unread_emails': unread_emails}
        return render(request, 'dashboard.html', context)
    
    except Exception as e:
        logger.error(f"Unexpected error in dashboard view: {e}")
        return HttpResponseRedirect(reverse('dashboard:error_view'))


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
