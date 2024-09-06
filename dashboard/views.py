import os
import json
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from tasks.models import Task
from jobs.models import Jobsearch
from emails.views import get_unread_emails
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Setup logger
logger = logging.getLogger(__name__)

def dashboard(request):
    logger.debug("Rendering dashboard view.")
    
    key = os.getenv('GOOGLE_API_KEY')
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    email_subjects, auth_url = get_unread_emails()
    logger.debug(f"Email subjects fetched: {email_subjects}")
    
    if auth_url:
        logger.debug(f"Redirecting to auth URL: {auth_url}")
        return redirect(auth_url)  # Redirect directly to the URL
    
    unread_email_count = len(email_subjects) if email_subjects else 0

    context = {
        'key': key,
        'locations': locations,
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
    }
    
    logger.debug(f"Context passed to template: {context}")
    
    return render(request, "dashboard/dashboard.html", context)


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

