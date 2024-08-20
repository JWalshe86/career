from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta

 # config for gmail api integration
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path

from .models import Jobsearch
from .forms import JobsearchForm, DateForm
from jobs.models import Jobsearch

# Define the scope and initialize other necessary variables
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]



def get_unread_emails():
    print("Fetching unread emails...")
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
           creds = flow.run_local_server(port=0)
       with open("token.json", "w") as token:
           token.write(creds.to_json())
    
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])

        email_data = []
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            headers = msg["payload"]["headers"]
            subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
            sender = next((header["value"] for header in headers if header["name"] == "From"), "No Sender")
            email_data.append({"subject": subject, "sender": sender})

        print(f"Extracted email data: {email_data}")
        return email_data
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []



def jobs_dashboard_with_emails(request):
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = []

    for a in eligible_locations:
        data = {
            'lat': float(a.lat),
            'lng': float(a.lng),
            'name': a.name
        }
        locations.append(data)

    email_subjects = get_unread_emails()
    print('Test print statement')  # Ensure this prints
    print('email_sub', email_subjects)
    return render(request, "jobs/jobs_dashboard.html", context={
        'key': key,
        'locations': locations,
        'email_subjects': email_subjects,
    })

def jobs_dashboard_basic(request):
    key = settings.GOOGLE_API_KEY
    eligible_locations = Jobsearch.objects.filter(place_id__isnull=False)
    locations = []

    for a in eligible_locations: 
        data = {
            'lat': float(a.lat), 
            'lng': float(a.lng), 
            'name': a.name
        }
        locations.append(data)
    
    return render(request, "jobs/jobs_dashboard.html", context={'key': key, 'locations': locations})



@login_required
def jobs_searched(request):
    if request.user.is_superuser:
        # Define time periods
        today = timezone.now()
        time_periods = {
            "one_week_ago": today - timedelta(days=7),
            "two_weeks_ago": today - timedelta(days=14),
            "one_month_ago": today - timedelta(days=30),
        }

        # Update statuses based on time periods
        status_updates = [
            ({"created_at__gt": time_periods["one_week_ago"], "status": "1week"}, "pending<wk"),
            ({"created_at__gt": time_periods["two_weeks_ago"], "created_at__lt": time_periods["one_week_ago"], "status": "1week"}, "pending<2wk"),
            ({"created_at__gt": time_periods["one_month_ago"], "created_at__lt": time_periods["two_weeks_ago"], "status": "1week"}, "pend<MONTH"),
            ({"created_at__lt": time_periods["one_month_ago"], "status": "pend+month"}, "not_proceeding"),
        ]

        for filters, new_status in status_updates:
            Jobsearch.objects.filter(**filters).update(status=new_status)

        # Annotate and order the jobs for display
        priority_mapping = {
            'offer': '-priority1',
            'interview': '-priority2',
            'pre_int_screen': '-priority3',
            'pending<wk': '-priority4',
            'pending<2wk': '-priority5',
            'pend<MONTH': '-priority6',
            'not_proceeding': '-priority7',
        }
        
        # Annotate jobs with priority levels
        jobs = Jobsearch.objects.all()
        for status, order in priority_mapping.items():
            jobs = jobs.annotate(**{f"priority{order[-1]}": Q(status=status)})

        # Order jobs by priority levels
        jobs = jobs.order_by(
            *priority_mapping.values()
        )

        context = {
            "jobs_searched": jobs,
        }
        return render(request, "jobs/job_searches.html", context)




# Data entry views start

@login_required
def jobsearch_detail(request, jobsearch_id):
        if request.user.is_superuser:
            """A view to show job search details"""

        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)

        context = {
            "jobsearch": jobsearch,
        }
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
                count = []

                for i in jobs:
                    # Convert i.created_at to date
                    created_date = i.created_at.date()

                    # Alerts if already applied for a role
                    if i.city == x['city'] and i.name == x['name'] and i.role == x['role']:
                        messages.warning(request, f"You've already applied for this job on {created_date}!")
                        return redirect(reverse('add_jobsearch'))

                    # Alerts if you've applied for 10 jobs in a day
                    if created_date == today:
                        count.append(1)

                if len(count) == 4:
                    messages.warning(request, f"Today: {today} you've applied for {len(count) +1} jobs!")

                data = form.save()
                messages.success(request, "Successfully added job application!")
                return redirect(reverse("jobs_searched"))

        else:
            form = JobsearchForm()

        template = "jobs/add_jobsearch.html"
        context = {"form": form}
        return render(request, template, context)


@login_required
def edit_jobsearch(request, jobsearch_id):
    if request.user.is_superuser:
        """Edit a plant in the store"""
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        if request.method == "POST":
            form = JobsearchForm(request.POST, request.FILES, instance=jobsearch)
            if form.is_valid():
                form.save()
                messages.success(request, "Successfully updated jobsearch!")
                return redirect(reverse("jobs_searched"))
            else:
                messages.error(
                    request,
                    "Failed to update jobsearch. Please ensure the form is valid.",
                )
        else:
            form = JobsearchForm(instance=jobsearch)
            messages.info(request, f"You are editing {jobsearch.name}")

        template = "jobs/edit_jobsearch.html"
        context = {
            "form": form,
            "jobsearch": jobsearch,
        }

        return render(request, template, context)

@login_required
def delete_jobsearch(request, jobsearch_id):
    if request.user.is_superuser:
        """Delete a jobsearch"""
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        jobsearch.delete()
        messages.success(request, "Jobsearch deleted!")
        return redirect(reverse("jobs_searched"))



def favs_display(request):
    
    favs = Jobsearch.objects.filter(favourite = True).values()

    context = {
        "favs": favs,
    }
        
    return render(request, "jobs/favourites.html", context)



