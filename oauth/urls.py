from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback, env_vars, oauth_login

urlpatterns = [
    # Path for the jobs dashboard with emails view
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    
    # Path for the OAuth login
    path('oauth/login/', oauth_login, name='oauth_login'),
    
    # Updated path for the OAuth2 callback to match the REDIRECT_URI
    path('jobs-dashboard/oauth2callback/', oauth2callback, name='oauth2callback'),
]

