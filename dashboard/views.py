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


def dashboard(request):
    """
    Render the dashboard with unread emails.
    """
    if not request.user.is_authenticated:
        return HttpResponse("User must be logged in to access this page.", status=403)

    try:
        email_subjects = get_unread_emails()
        unread_email_count = len(email_subjects) if email_subjects else 0

        context = {
            'email_subjects': email_subjects,
            'unread_email_count': unread_email_count,
        }
        return render(request, "dashboard/dashboard.html", context)

    except Exception as e:
        logger.error(f"Error in getting unread emails or rendering dashboard: {e}")
        return HttpResponse("An unexpected error occurred while fetching emails.", status=500)



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

