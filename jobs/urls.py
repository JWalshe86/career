from django.urls import path
from map.views import MapView  # Import MapView from the map app
from .views import (
    jobs_dashboard_with_emails, 
    jobs_dashboard_basic,  # This view is imported but not used in urlpatterns
    job_search_view, 
    oauth2callback,  # Import the OAuth2 callback view
    show_env_var
)

from . import views  # Import all views from the current app

urlpatterns = [
    path('dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),  # Dashboard view with emails
    path('show-env/', show_env_var, name='show_env_var'),  # Show environment variable
    path("favs/", views.favs_display, name="favs_display"),  # Display favorite items
    path("map/", MapView.as_view(), name='my_map_view'),  # Map view from the map app
    path("jobs_searched/", views.jobs_searched, name="jobs_searched"),  # Jobs searched view
    path("add_jobsearch/", views.add_jobsearch, name="add_jobsearch"),  # Add job search view
    path("<int:jobsearch_id>/", views.jobsearch_detail, name="jobsearch_detail"),  # Job search detail view
    path("edit/<int:jobsearch_id>/", views.edit_jobsearch, name="edit_jobsearch"),  # Edit job search view
    path("delete/<int:jobsearch_id>/", views.delete_jobsearch, name="delete_jobsearch"),  # Delete job search view
    path("job-search/", job_search_view, name="job_search_view"),  # Job search view
    path("oauth2callback/", oauth2callback, name="oauth2callback"),  # OAuth2 callback view
]

