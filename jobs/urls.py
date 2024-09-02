from django.urls import path
from .views import jobsearch_detail, add_jobsearch, edit_jobsearch, delete_jobsearch, job_search_view, favs_display

urlpatterns = [
    path('jobsearch/<int:jobsearch_id>/', jobsearch_detail, name='jobsearch_detail'),
    path('add/', add_jobsearch, name='add_jobsearch'),
    path('edit/<int:jobsearch_id>/', edit_jobsearch, name='edit_jobsearch'),
    path('delete/<int:jobsearch_id>/', delete_jobsearch, name='delete_jobsearch'),
    path('search/', job_search_view, name='job_search_view'),
    path('favorites/', favs_display, name='favs_display'),
]

