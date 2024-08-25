from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.utils import timezone
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

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
logger = logging.getLogger(__name__)

def refresh_access_token(refresh_token):
    logger.debug("Starting token refresh process.")
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET
    }
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return None


def get_oauth2_authorization_url():
    logger.debug("Starting to generate OAuth2 authorization URL.")
    
    # Log the settings and scopes used
    logger.debug("GOOGLE_CREDENTIALS_PATH: %s", settings.GOOGLE_CREDENTIALS_PATH)
    logger.debug("SCOPES: %s", SCOPES)
    
    try:
        # Create the OAuth2 flow object
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        logger.debug("OAuth2 flow created successfully.")
        
        # Log the flow details
        logger.debug("Flow client secrets file: %s", settings.GOOGLE_CREDENTIALS_PATH)
        logger.debug("Flow scopes: %s", SCOPES)
        
        # Generate the authorization URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        logger.debug("Generated authorization URL and state.")
        
        # Log the generated URL and state
        logger.info("Generated authorization URL: %s", auth_url)
        logger.debug("Generated state: %s", state)
        
        return auth_url
    
    except Exception as e:
        # Log detailed error information
        logger.error("Error generating authorization URL: %s", e)
        logger.error("Type of error: %s", type(e))
        if hasattr(e, 'response'):
            logger.error("Response content: %s", e.response.content)
        raise


def oauth2callback(request):
    logger.debug("Handling OAuth2 callback.")

    try:
        # Initialize OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            SCOPES
        )
        logger.debug("OAuth2 flow initialized successfully.")

        # Set redirect URI
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        logger.debug("Redirect URI set to: %s", settings.GOOGLE_REDIRECT_URI)

        # Fetch authorization response URL from the request
        authorization_response = request.build_absolute_uri()
        logger.debug("Authorization response URL: %s", authorization_response)

        # Check if the authorization response is None
        if not authorization_response:
            raise RuntimeError("Authorization response not received. OAuth2 flow may not have completed successfully.")

        # Fetch the token
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials
        logger.debug("Token fetched successfully.")
        logger.debug("Token details: %s", creds.to_json())

        # Save the token to a file
        with open(settings.TOKEN_FILE_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        logger.info("Token saved to %s", settings.TOKEN_FILE_PATH)

        # Redirect to the dashboard
        return redirect(reverse('jobs_dashboard_with_emails'))

    except Exception as e:
        logger.error("Error in OAuth callback: %s", e)
        logger.error("Type of error: %s", type(e))
        if hasattr(e, 'response') and e.response:
            logger.error("Response content: %s", e.response.content)
        return redirect(reverse('jobs_dashboard_with_emails'))


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_unread_emails():
    creds = None

    if 'DYNO' in os.environ:  # Heroku environment
        # Load credentials from environment variables
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        google_credentials = json.loads(google_credentials_json)
        if not google_credentials.get('web'):
            logger.error("No credentials found in environment variables.")
            return [], None

        creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
        logger.debug("Loaded credentials from environment variables")
    else:  # Local environment
        # Check if token file exists and load credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.debug("Loaded credentials from token.json")
        else:
            # If no token file, run the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            logger.debug("Obtained credentials from OAuth flow")

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token.json")

    # Refresh the token if necessary
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            if not 'DYNO' in os.environ:  # Only save the token file locally
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            logger.info("Credentials refreshed and saved")
        except Exception as e:
            logger.error("Error refreshing credentials: %s", e)
            auth_url = get_oauth2_authorization_url()
            return [], auth_url

    # If no valid credentials, return to auth
    if not creds or not creds.valid:
        logger.debug("No valid credentials found. Redirecting to authorization URL.")
        auth_url = get_oauth2_authorization_url()
        return [], auth_url

    # Try to fetch unread emails
    try:
        service = build("gmail", "v1", credentials=creds)
        query = "is:unread -category:social -category:promotions"
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

        logger.info("Processed unread emails: %s", unread_emails)
        return unread_emails, None

    except HttpError as error:
        logger.error("An error occurred while fetching emails: %s", error)
        return [], None
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        return [], None


@login_required
def jobs_dashboard_with_emails(request):
    logger.debug("Rendering jobs dashboard with emails.")
    email_subjects, auth_url = get_unread_emails()
    if auth_url:
        logger.debug("Redirecting to authorization URL: %s", auth_url)
        return redirect(auth_url)

    unread_email_count = len(email_subjects) if email_subjects else 0

    context = {
        'key': settings.GOOGLE_API_KEY,
        'locations': [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in Jobsearch.objects.filter(place_id__isnull=False)],
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
    }
    logger.debug("Context for rendering: %s", context)
    return render(request, "jobs/jobs_dashboard.html", context)

@login_required
def jobs_dashboard_basic(request):
    logger.debug("Rendering basic jobs dashboard.")
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    return render(request, "jobs/jobs_dashboard.html", context={'key': key, 'locations': locations})

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
            ({"created_at__gt": time_periods["one_week_ago"], "status": "1week"}, "pending<wk"),
            ({"created_at__gt": time_periods["two_weeks_ago"], "created_at__lt": time_periods["one_week_ago"], "status": "1week"}, "pending<2wk"),
            ({"created_at__gt": time_periods["one_month_ago"], "created_at__lt": time_periods["two_weeks_ago"], "status": "1week"}, "pend<MONTH"),
            ({"created_at__lt": time_periods["one_month_ago"], "status": "pend+month"}, "not_proceeding"),
        ]

        for filters, new_status in status_updates:
            Jobsearch.objects.filter(**filters).update(status=new_status)
            logger.debug("Updated jobs with filters %s to status %s", filters, new_status)

        jobs_applied_today = Jobsearch.objects.filter(created_at__date=today)

        priority_mapping = {
            'offer': '-priority1',
            'interview': '-priority2',
            'pre_int_screen': '-priority3',
            'pending<wk': '-priority4',
            'pending<2wk': '-priority5',
            'pend<MONTH': '-priority6',
            'not_proceeding': '-priority7',
        }

        jobs = Jobsearch.objects.all()
        for status, order in priority_mapping.items():
            jobs = jobs.annotate(**{f"priority{order[-1]}": Q(status=status)})

        jobs = jobs.order_by(*priority_mapping.values())

        for job in jobs:
            job.background_color = {
                "pending<wk": 'yellow',
                "pending<2wk": 'orange',
                "pend<MONTH": 'purple',
                "not_proceeding": 'red',
                "pre_int_screen": '#83d7ad',
                "interview": 'blue',
                "offer": 'green',
            }.get(job.status, 'white')

        context = {
            "jobs_searched": jobs,
            "jobs_applied_today": jobs_applied_today,
            "tasks": tasks,
            "form": form,
        }
        logger.debug("Context for jobs_searched rendering: %s", context)
        return render(request, "jobs/job_searches.html", context)

@login_required
def jobsearch_detail(request, jobsearch_id):
    logger.debug("Rendering job search detail for ID: %s", jobsearch_id)
    if request.user.is_superuser:
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        context = {"jobsearch": jobsearch}
        return render(request, "jobs/jobsearch_detail.html", context)

@login_required
def add_jobsearch(request):
    logger.debug("Handling add jobsearch.")
    if request.user.is_superuser:
        if request.method == "POST":
            form = JobsearchForm(request.POST, request.FILES)
            if form.is_valid():
                jobs = Jobsearch.objects.all()
                x = request.POST
                today = date.today()
                count = [1 for i in jobs if i.city == x['city'] and i.name == x['name'] and i.role == x['role'] and i.created_at.date() == today]

                if count:
                    messages.warning(request, f"You've already applied for this job on {i.created_at.date()}!")
                    logger.warning("User has already applied for this job on %s.", i.created_at.date())
                    return redirect(reverse('add_jobsearch'))

                if len(count) >= 10:
                    messages.warning(request, "You've reached the limit of 10 applications per day.")
                    logger.warning("User has reached the limit of 10 applications per day.")
                    return redirect(reverse('add_jobsearch'))

                form.save()
                messages.success(request, "Job search added successfully!")
                logger.info("Job search added successfully.")
                return redirect(reverse('jobs_searched'))
        else:
            form = JobsearchForm()
        return render(request, "jobs/add_jobsearch.html", {'form': form})

@login_required
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

@login_required
def delete_jobsearch(request, jobsearch_id):
    logger.debug("Handling delete jobsearch for ID: %s", jobsearch_id)
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        jobsearch.delete()
        messages.success(request, "Job search deleted successfully!")
        logger.info("Job search deleted successfully for ID: %s", jobsearch_id)
        return redirect(reverse('jobs_searched'))
    return render(request, "jobs/delete_jobsearch.html", {'jobsearch': jobsearch})

@login_required
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

@login_required
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

