from django.urls import path
from .views import display_emails

urlpatterns = [
    path('display_emails/', display_emails, name='display_emails'),
]


