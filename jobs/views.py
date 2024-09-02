from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import timedelta
import logging

from tasks.models import Task
from .models import Jobsearch
from .forms import JobsearchForm
from tasks.forms import TaskForm

# Setup logger
logger = logging.getLogger(__name__)

@login_required
def jobsearch_detail(request, jobsearch_id):
    """Render job search detail."""
    logger.debug(f"Rendering job search detail for ID: {jobsearch_id}")
    if request.user.is_superuser:
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        context = {"jobsearch": jobsearch}
        return render(request, "jobs/jobsearch_detail.html", context)
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect(reverse('job_search_view'))

@login_required
def add_jobsearch(request):
    """Handle addition of a new job search."""
    logger.debug("Handling add jobsearch.")

    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect(reverse('job_search_view'))

    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                today = timezone.now().date()
                jobsearch_data = form.cleaned_data

                # Log form data for debugging
                logger.debug(f"Form data: {jobsearch_data}")

                # Save the job search form
                form.save()

                # Count the number of jobs applied for today
                today_job_count = Jobsearch.objects.filter(created_at__date=today).count()

                # Prepare the success message
                success_message = f"Job search added successfully! You've applied for {today_job_count} jobs today."

                # Check if the user has applied for 5 jobs today
                if today_job_count == 5:
                    success_message += " Congratulations! You've reached 5 job applications today."

                # Display the success message
                messages.success(request, success_message)
                logger.info("Job search added successfully.")
                return redirect(reverse('job_search_view'))

            except Exception as e:
                logger.error(f"An error occurred while adding job search: {str(e)}")
                messages.error(request, "An error occurred while processing your request.")
                return redirect(reverse('add_jobsearch'))
        else:
            logger.debug("Form is not valid.")
            # Log form errors for debugging
            logger.debug(f"Form errors: {form.errors}")
            return render(request, "jobs/add_jobsearch.html", {'form': form})
    else:
        form = JobsearchForm()

    return render(request, "jobs/add_jobsearch.html", {'form': form})

@login_required
def edit_jobsearch(request, jobsearch_id):
    """Handle editing of an existing job search."""
    logger.debug("Handling edit jobsearch for ID: %s", jobsearch_id)
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES, instance=jobsearch)
        if form.is_valid():
            form.save()
            messages.success(request, "Job search updated successfully!")
            logger.info("Job search updated successfully for ID: %s", jobsearch_id)
            return redirect(reverse('jobsearch_detail', args=[jobsearch_id]))
    else:
        form = JobsearchForm(instance=jobsearch)
    return render(request, "jobs/edit_jobsearch.html", {'form': form, 'jobsearch': jobsearch})

@login_required
def delete_jobsearch(request, jobsearch_id):
    """Handle deletion of a job search."""
    logger.debug(f"Attempting to delete job search with ID: {jobsearch_id}")

    if request.method == 'POST':
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        jobsearch.delete()
        messages.success(request, _("Job search deleted successfully."))
        return redirect(reverse('job_search_view'))
    else:
        messages.error(request, _("Invalid request method."))
        return redirect(reverse('job_search_view'))

def job_search_view(request):
    """Render job search view."""
    logger.debug("Rendering job search view.")
    job_search_view = Jobsearch.objects.all()
    for job in job_search_view:
        job.background_color = {
            "pending<wk": 'yellow',
            "pending<2wk": 'orange',
            "pend<MONTH": 'purple',
            "not_proceeding": 'red',
            "pre_int_screen": '#83d7ad',
            "interview": 'blue',
            "offer": 'green',
        }.get(job.status, 'white')

    return render(request, 'jobs/job_search_view.html', {'job_search_view': job_search_view})

def favs_display(request):
    """Render favorite jobs display."""
    logger.debug("Rendering favorite jobs display.")
    if request.user.is_authenticated:
        favorite_jobs = Jobsearch.objects.filter(is_favorite=True)
        context = {
            'favorite_jobs': favorite_jobs
        }
        return render(request, 'jobs/favorites.html', context)
    else:
        messages.error(request, "You must be logged in to view your favorites.")
        return redirect(reverse('login'))

