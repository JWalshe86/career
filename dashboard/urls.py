# dashboard/urls.py
from django.urls import path
from .views import dashboard, dashboard_searched, error_view

app_name = 'dashboard'
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('searched/', dashboard_searched, name='dashboard_searched'),
    path('error/', error_view, name='error_view'),  # Ensure this path is defined
]

