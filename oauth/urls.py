from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback, env_vars, oauth_login

urlpatterns = [
    # Path for the jobs dashboard with emails view
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    
    # Path for the OAuth login
    path('oauth/login/', oauth_login, name='oauth_login'),
    
    # Path for the OAuth2 callback
    path('oauth/callback/', oauth2callback, name='oauth2callback'),
]

