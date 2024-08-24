from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta
import requests
import os
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
        logger.error("Error refreshing token: %s", e)
        return None


logger = logging.getLogger(__name__)


def get_oauth2_authorization_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_PATH,
        SCOPES
    )
    logger.info("Creating authorization URL...")
    
    # Explicitly pass the redirect_uri
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        redirect_uri=settings.GOOGLE_REDIRECT_URI  # Ensure this matches your Google API Console settings
    )
    
    logger.info(f"Authorization URL: {auth_url}")
    return auth_url


def oauth2callback(request):
    flow = InstalledAppFlow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_PATH,
        SCOPES
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI  # Set the redirect URI explicitly
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    creds = flow.credentials
    with open(settings.TOKEN_FILE_PATH, "w") as token:
        token.write(creds.to_json())
    
    return redirect(reverse('jobs_dashboard_with_emails'))


def get_unread_emails():
    creds = None
    if os.path.exists(settings.TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(settings.TOKEN_FILE_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(settings.TOKEN_FILE_PATH, "w") as token:
                token.write(creds.to_json())
        else:
            auth_url = get_oauth2_authorization_url()
            return [], auth_url  # Return an empty list and the auth URL

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
        query += "".join(f" -from:{sender}" for sender in excluded_senders)
        
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            logger.info("No unread messages found.")
            return [], None  # Return an empty list and no auth URL

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

        return unread_emails, None

    except HttpError as error:
        logger.error("An HTTP error occurred: %s", error)
        return [], None
    except Exception as error:
        logger.error("An error occurred: %s", error)
        return [], None


@login_required
def jobs_dashboard_with_emails(request):
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    email_subjects, auth_url = get_unread_emails()
    if auth_url:
        return redirect(auth_url)  # Redirect if authorization URL is provided

    unread_email_count = len(email_subjects) if email_subjects else 0

    return render(request, "jobs/jobs_dashboard.html", context={
        'key': key,
        'locations': locations,
        'email_subjects': email_subjects,
        'unread_email_count': unread_email_count,
    })

@login_required
def jobs_dashboard_basic(request):
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = [{'lat': float(a.lat), 'lng': float(a.lng), 'name': a.name} for a in eligible_locations]
    
    return render(request, "jobs/jobs_dashboard.html", context={'key': key, 'locations': locations})

@login_required
def jobs_searched(request):
    if request.user.is_superuser:
        today = timezone.now().date()
        tasks = Task.objects.all()
        form = TaskForm()

        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                form.save()
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
        return render(request, "jobs/job_searches.html", context)

@login_required
def jobsearch_detail(request, jobsearch_id):
    if request.user.is_superuser:
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        context = {"jobsearch": jobsearch}
        return render(request, "jobs/jobsearch_detail.html", context)

@login_required
def add_jobsearch(request):
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
                    return redirect(reverse('add_jobsearch'))

                if len(count) >= 10:
                    messages.warning(request, "You've reached the limit of 10 applications per day.")
                    return redirect(reverse('add_jobsearch'))

                form.save()
                messages.success(request, "Job search added successfully!")
                return redirect(reverse('jobs_searched'))
        else:
            form = JobsearchForm()
        return render(request, "jobs/add_jobsearch.html", {'form': form})

@login_required
def edit_jobsearch(request, jobsearch_id):
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES, instance=jobsearch)
        if form.is_valid():
            form.save()
            messages.success(request, "Job search updated successfully!")
            return redirect(reverse('jobsearch_detail', args=[jobsearch_id]))
    else:
        form = JobsearchForm(instance=jobsearch)
    return render(request, "jobs/edit_jobsearch.html", {'form': form, 'jobsearch': jobsearch})

@login_required
def delete_jobsearch(request, jobsearch_id):
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        jobsearch.delete()
        messages.success(request, "Job search deleted successfully!")
        return redirect(reverse('jobs_searched'))
    return render(request, "jobs/delete_jobsearch.html", {'jobsearch': jobsearch})

@login_required
def job_search_view(request):
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
    if request.user.is_authenticated:
        # Assuming the favorite jobs are marked by a boolean field 'is_favorite' in Jobsearch model
        favorite_jobs = Jobsearch.objects.filter(is_favorite=True)
        context = {
            'favorite_jobs': favorite_jobs,
        }
        return render(request, 'jobs/favs_display.html', context)
    else:
        return redirect(reverse('login'))

