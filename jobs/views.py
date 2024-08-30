from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import date, timedelta
import requests
import os
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from tasks.models import Task
from .models import Jobsearch
from .forms import JobsearchForm
from tasks.forms import TaskForm

# Define SCOPES once
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Setup logger
logger = logging.getLogger(__name__)

def show_env_var(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

def make_google_api_request():
    try:
        token = os.getenv("GOOGLE_ACCESS_TOKEN")
        response = requests.get(
            "https://www.googleapis.com/gmail/v1/users/me/messages",
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 401:
            new_token, _ = refresh_google_token()
            response = requests.get(
                "https://www.googleapis.com/gmail/v1/users/me/messages",
                headers={'Authorization': f'Bearer {new_token}'}
            )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"An error occurred while making the Google API request: {e}")
        return {}

def get_oauth2_authorization_url():
    logger.debug("Generating OAuth2 authorization URL.")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise

def oauth2callback(request):
    logger.debug("Handling OAuth2 callback.")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        authorization_response = request.build_absolute_uri()
        
        if not authorization_response:
            raise RuntimeError("Authorization response not received.")
        
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials
        with open(settings.TOKEN_FILE_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        logger.info(f"Token saved to {settings.TOKEN_FILE_PATH}")
        return redirect(reverse('jobs_dashboard_with_emails'))
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return redirect(reverse('jobs_dashboard_with_emails'))

def get_unread_emails():
    creds = None

    if 'DYNO' in os.environ:  # Heroku environment
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        try:
            google_credentials = json.loads(google_credentials_json)
            creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
            logger.debug("Loaded credentials from environment variables.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for Google credentials: {e}")
            return [], None
    else:  # Local environment
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.debug("Loaded credentials from token.json.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token.json.")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            if not 'DYNO' in os.environ:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            logger.info("Credentials refreshed and saved.")
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            auth_url = get_oauth2_authorization_url()
            return [], auth_url

    if not creds or not creds.valid:
        logger.debug("No valid credentials found. Redirecting to authorization URL.")
        auth_url = get_oauth2_authorization_url()
        return [], auth_url

    try:
        service = build("gmail", "v1", credentials=creds)
        excluded_senders = [
            "no-reply@usebubbles.com",
            "chandeep@2toucans.com",
            "craig@itcareerswitch.co.uk",
            "no-reply@swagapp.com",
            "no-reply@fathom.video",
            "mailer@jobleads.com",
            "careerservice@email.jobleads.com"
        ]
        query = "is:unread -category:social -category:promotions"
        for sender in excluded_senders:
            query += f" -from:{sender}"
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get('messages', [])
        
        unread_emails = []
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            snippet = msg['snippet']
            email_data = {
                'id': message['id'],
                'snippet': snippet,
                'sender': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'),
                'subject': next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'),
                'highlight': 'highlight' if 'unfortunately' in snippet.lower() else ''
            }
            unread_emails.append(email_data)
        
        logger.info(f"Processed unread emails: {unread_emails}")
        return unread_emails, None
    except HttpError as error:
        logger.error(f"An error occurred while fetching emails: {error}")
        return [], None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return [], None

@login_required
def jobs_dashboard_with_emails(request):
    logger.debug("Rendering jobs dashboard with emails.")
    
    email_subjects, auth_url = get_unread_emails()
    if auth_url:
        logger.debug(f"Redirecting to authorization URL: {auth_url}")
        return redirect(auth_url)

    unread_email_count = len(email_subjects) if email_subjects else 0
    tasks = Task.objects.all()
    
    # Debugging output
    for task in tasks:
        logger.debug(f"Task ID: {task.id}, Title: {task.title}")

    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in Jobsearch.objects.filter(place_id__isnull=False)]
    context = {
        'key': settings.GOOGLE_API_KEY,
        'locations': locations,
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
        'tasks': tasks,
    }
    logger.debug(f"Context for rendering: {context}")
    return render(request, "jobs/jobs_dashboard.html", context)

@login_required
def jobs_dashboard_basic(request):
    logger.debug("Rendering basic jobs dashboard.")
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    return render(request, "jobs/jobs_dashboard.html", context={'key': key, 'locations': locations})

@login_required
def jobsearch_detail(request, jobsearch_id):
    logger.debug(f"Rendering job search detail for ID: {jobsearch_id}")
    if request.user.is_superuser:
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        context = {"jobsearch": jobsearch}
        return render(request, "jobs/jobsearch_detail.html", context)
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect(reverse('jobs_dashboard_basic'))

@login_required
def jobs_searched(request):
    logger.debug("Rendering jobs searched dashboard.")

    if request.user.is_superuser:
        today = timezone.now().date()
        tasks = Task.objects.all()
        form = TaskForm()

        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                form.save()
                logger.info("Task form submitted and saved.")
                return redirect(reverse('jobs_searched'))

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

        return render(request, "jobs/jobs_searched.html", context)


@login_required
def add_jobsearch(request):
    logger.debug("Handling add jobsearch.")

    # Ensure the user is a superuser, otherwise, redirect them
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect(reverse('jobs_searched'))

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
                return redirect(reverse('jobs_searched'))

            except Exception as e:
                logger.error(f"An error occurred while adding job search: {str(e)}")
                messages.error(request, "An error occurred while processing your request.")
                return redirect(reverse('add_jobsearch'))
        else:
            logger.debug("Form is not valid.")
            # Log form errors for debugging
            logger.debug(f"Form errors: {form.errors}")
            # If the form is not valid, return to the same page with form errors
            return render(request, "jobs/add_jobsearch.html", {'form': form})
    else:
        # If not a POST request, just render the empty form
        form = JobsearchForm()

    # Render the form in case of non-POST requests
    return render(request, "jobs/add_jobsearch.html", {'form': form})


def edit_jobsearch(request, jobsearch_id):
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



logger = logging.getLogger(__name__)




@login_required
def delete_jobsearch(request, jobsearch_id):
    logger.debug(f"Attempting to delete job search with ID: {jobsearch_id}")
    
    if request.method == 'POST':
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        jobsearch.delete()
        messages.success(request, _("Job search deleted successfully."))
        return redirect(reverse('jobs_dashboard_with_emails'))
    else:
        messages.error(request, _("Invalid request method."))
        return redirect(reverse('jobs_dashboard_with_emails'))


def job_search_view(request):
    logger.debug("Rendering job search view.")
    jobs_searched = Jobsearch.objects.all()
    for job in jobs_searched:
        job.background_color = {
            "pending<wk": 'yellow',
            "pending<2wk": 'orange',
            "pend<MONTH": 'purple',
            "not_proceeding": 'red',
            "pre_int_screen": '#83d7ad',
            "interview": 'blue',
            "offer": 'green',
        }.get(job.status, 'white')

    return render(request, 'jobs/job_search_view.html', {'jobs_searched': jobs_searched})

def favs_display(request):
    logger.debug("Rendering favorite jobs display.")
    if request.user.is_authenticated:
        favorite_jobs = Jobsearch.objects.filter(is_favorite=True)
        context = {
            'favorite_jobs': favorite_jobs,
        }
        return render(request, 'jobs/favs_display.html', context)
    else:
        logger.debug("User is not authenticated, redirecting to login.")
        return redirect(reverse('login'))
