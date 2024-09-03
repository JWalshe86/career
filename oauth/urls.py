# oauth/urls.py
from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback, env_vars, oauth_login

urlpatterns = [
    # Updated the path for the jobs dashboard with emails view
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    path('oauth/login/', oauth_login, name='oauth_login'),
    path('env-vars/', env_vars, name='env_vars'),
    # Updated the path for the OAuth2 callback to reflect the new structure
    path('jobs-dashboard/oauth2callback/', oauth2callback, name='oauth2callback'),
]

