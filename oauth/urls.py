from django.urls import path
from .views import jobs_dashboard_with_emails_or_callback, oauth_login

urlpatterns = [
    # Combined path for both the jobs dashboard and OAuth2 callback
    path('oauth/jobs-dashboard/', jobs_dashboard_with_emails_or_callback, name='jobs_dashboard_or_callback'),
    
    # Path for the OAuth login
    path('oauth/login/', oauth_login, name='oauth_login'),
]

