from django.urls import path

from . import views

urlpatterns = [
          path("display_data/", views.display_data, name="display_data"),
          path("add_data/", views.add_data, name="add_data"),
          path("^<int:jobsearch_id>/$", views.jobsearch_detail, name="jobsearch_detail"),
          path("edit/<int:jobsearch_id>/", views.edit_jobsearch, name="edit_jobsearch"),
        ]
