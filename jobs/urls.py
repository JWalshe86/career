from django.urls import path

from . import views

urlpatterns = [
          path("jobsdashboard/", views.display_lkdata, name="display_lkdata"),
          path("add_lkdata/", views.add_lkdata, name="add_lkdata"),
          path("jobs_searched/", views.jobs_searched, name="jobs_searched"),
          path("add_jobsearch/", views.add_jobsearch, name="add_jobsearch"),
          path("^<int:jobsearch_id>/$", views.jobsearch_detail, name="jobsearch_detail"),
          path("edit/<int:jobsearch_id>/", views.edit_jobsearch, name="edit_jobsearch"),
          path("delete/<int:jobsearch_id>/", views.delete_jobsearch, name="delete_jobsearch"),
        ]
