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



def show_env_var(request):
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    return HttpResponse(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
logger = logging.getLogger(__name__)



def make_google_api_request():
    try:
        # Attempt the request with the current token
        response = requests.get("https://www.googleapis.com/gmail/v1/users/me/messages", headers={
            'Authorization': f'Bearer {os.getenv("GOOGLE_ACCESS_TOKEN")}'
        })
        if response.status_code == 401:
            # Token expired, refresh it
            new_token, _ = refresh_google_token()
            # Retry the request with the new token
            response = requests.get("https://www.googleapis.com/gmail/v1/users/me/messages", headers={
                'Authorization': f'Bearer {new_token}'
            })
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
data = make_google_api_request()


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
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', '{}')
        try:
            google_credentials = json.loads(google_credentials_json)
            if not google_credentials.get('web'):
                logger.error("No credentials found in environment variables.")
                return [], None

            creds = Credentials.from_authorized_user_info(google_credentials, SCOPES)
            logger.debug("Loaded credentials from environment variables.")
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON for Google credentials: %s", e)
            return [], None
    else:  # Local environment
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.debug("Loaded credentials from token.json.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            logger.debug("Obtained credentials from OAuth flow.")

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
            logger.error("Error refreshing credentials: %s", e)
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

        logger.debug("Fetched messages: %s", messages)

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


def jobs_dashboard_with_emails(request):
    logger.debug("Rendering jobs dashboard with emails.")
    logger.debug("Request: %s", request)
  
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



def jobs_dashboard_basic(request):
    logger.debug("Rendering basic jobs dashboard.")
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    return render(request, "jobs/jobs_dashboard.html", context={'key': key, 'locations': locations})


def jobsearch_detail(request, jobsearch_id):
    logger.debug("Rendering job search detail for ID: %s", jobsearch_id)
    if request.user.is_superuser:
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        context = {"jobsearch": jobsearch}
        return render(request, "jobs/jobsearch_detail.html", context)


# Setup logger
logger = logging.getLogger(__name__)


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

        # Set background color based on status
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
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect(reverse('jobs_dashboard_basic'))




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
    logger.debug("Handling delete jobsearch for ID: %s with method: %s", jobsearch_id, request.method)
    
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    
    if request.method == "POST":
        jobsearch.delete()
        messages.success(request, "Job search deleted successfully!")
        logger.info("Job search deleted successfully for ID: %s", jobsearch_id)
        return redirect(reverse('jobs_searched'))
    
    # Optionally handle GET requests here if you want to display a confirmation page
    # return render(request, "confirm_delete.html", {'jobsearch': jobsearch})

    # For now, redirect on non-POST requests
    messages.error(request, "Invalid request method.")
    return redirect(reverse('jobs_searched'))




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

