from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback, env_vars, oauth_login

urlpatterns = [
    # Updated the path for the jobs dashboard with emails view
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    path('oauth/login/', oauth_login, name='oauth_login'),
    # Update the path for the OAuth2 callback to match the redirect URI
    path('oauth/jobs-dashboard/', oauth2callback, name='oauth2callback'),
]

