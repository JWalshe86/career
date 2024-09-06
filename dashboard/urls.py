# dashboard/urls.py

from django.urls import path
from .views import dashboard, dashboard_searched

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Updated the path for the main dashboard view
    path('searched/', dashboard_searched, name='dashboard_searched'),
]

