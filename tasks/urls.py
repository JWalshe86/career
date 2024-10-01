from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),  # URL to list all tasks
    path('<int:pk>/delete_task/', views.delete_task, name='delete_task'),  # URL to delete a task
    path('<int:task_id>/toggle/', views.toggle_task_complete, name='toggle_complete'),  # URL to toggle task completion
    path('get/', views.get_task, name='get_task'),  # URL for fetching a task
]

