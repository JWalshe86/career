from django.urls import path
from .views import email_dashboard

urlpatterns = [
    path('dashboard/', email_dashboard, name='email_dashboard'),
]


