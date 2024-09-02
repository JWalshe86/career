# oauth/urls.py

from django.urls import path
from .views import oauth2callback, jobs_dashboard_with_emails

urlpatterns = [
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
]

