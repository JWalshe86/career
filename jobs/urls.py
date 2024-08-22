# urls.py

from django.urls import path
from map.views import MapView  # Import MapView from the map app
from .views import (
    jobs_dashboard_with_emails, 
    jobs_dashboard_basic, 
    job_search_view, 
    jobs_searched, 
    add_jobsearch, 
    jobsearch_detail, 
    edit_jobsearch, 
    delete_jobsearch, 
    favs_display
)

urlpatterns = [
    path('dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    path('dashboard/basic/', jobs_dashboard_basic, name='jobs_dashboard_basic'),  # Added the basic dashboard view
    path('favs/', favs_display, name='favs_display'),
    path('map/', MapView.as_view(), name='my_map_view'),  # Use MapView from map app
    path('jobs_searched/', jobs_searched, name='jobs_searched'),
    path('add_jobsearch/', add_jobsearch, name='add_jobsearch'),
    path('edit/<int:jobsearch_id>/', edit_jobsearch, name='edit_jobsearch'),
    path('delete/<int:jobsearch_id>/', delete_jobsearch, name='delete_jobsearch'),
    path('<int:jobsearch_id>/', jobsearch_detail, name='jobsearch_detail'),
    path('job-search/', job_search_view, name='job_search_view'),  # Add job_search_view
]

