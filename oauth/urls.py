from django.urls import path
from .views import jobs_dashboard_with_emails_or_callback, oauth_login, env_vars

urlpatterns = [
    # Path for the jobs dashboard with emails or OAuth2 callback
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails_or_callback, name='jobs_dashboard_with_emails'),
    
    # Path for the OAuth login
    path('oauth/login/', oauth_login, name='oauth_login'),
    
    # Path for the environment variables
    path('env-vars/', env_vars, name='env_vars'),
]

