from django.urls import path
from .views import oauth_login, jobs_dashboard_with_emails_or_callback

urlpatterns = [
    path('login/', oauth_login, name='oauth_login'),
    path('jobs-dashboard/', jobs_dashboard_with_emails_or_callback, name='jobs_dashboard_with_emails'),
]

