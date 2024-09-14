# dashboard/urls.py
from django.urls import path
from .views import dashboard, dashboard_searched

app_name = 'dashboard'
urlpatterns = [
    path('', dashboard, name='dashboard'),  # Updated the path for the main dashboard view
    path('searched/', dashboard_searched, name='dashboard_searched'),
    path('error/', views.error_view, name='error_view'),
]

