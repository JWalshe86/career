# oauth/urls.py
from django.urls import path
from .views import jobs_dashboard_with_emails, oauth2callback

urlpatterns = [
    path('jobs-dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
]

