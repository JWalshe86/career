from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),  # URL to list all tasks
    path('create/', views.create_task, name='create_task'),  # URL to create a new task
    path('<int:pk>/update_task/', views.update_task, name='update_task'),  # URL to update an existing task
    path('<int:pk>/delete_task/', views.delete_task, name='delete_task'),  # URL to delete a task
    path('<int:task_id>/toggle/', views.toggle_task_complete, name='toggle_complete'),  # URL to toggle task completion
]

