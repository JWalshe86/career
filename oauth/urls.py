# oauth/urls.py
from django.urls import path
from .views import oauth2callback

urlpatterns = [
    path('jobs-dashboard/oauth2callback/', oauth2callback, name='oauth2callback'),
]

