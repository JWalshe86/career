# oauth/urls.py
from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback

urlpatterns = [
    # Updated the path for the jobs dashboard with emails view
    path('jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),

    # Updated the path for the OAuth2 callback to reflect the new structure
    path('jobs-dashboard/oauth2callback/', oauth2callback, name='oauth2callback'),
]

