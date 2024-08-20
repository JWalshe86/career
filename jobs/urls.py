from django.urls import path
from map.views import MapView  # Import MapView from the map app
from .views import jobs_dashboard_with_emails, jobs_dashboard_basic

from . import views

urlpatterns = [
    path('dashboard/', jobs_dashboard_with_emails, name='jobs_dashboard_with_emails'),
    path("favs/", views.favs_display, name="favs_display"),
    path("map/", MapView.as_view(), name='my_map_view'),  # Use MapView from map app
    path("jobs_searched/", views.jobs_searched, name="jobs_searched"),
    path("add_jobsearch/", views.add_jobsearch, name="add_jobsearch"),
    path("<int:jobsearch_id>/", views.jobsearch_detail, name="jobsearch_detail"),
    path("edit/<int:jobsearch_id>/", views.edit_jobsearch, name="edit_jobsearch"),
    path("delete/<int:jobsearch_id>/", views.delete_jobsearch, name="delete_jobsearch"),
]

