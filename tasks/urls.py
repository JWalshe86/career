from django.urls import path
from . import views

app_name = 'tasks'  # Add this line to set the namespace

urlpatterns = [
    path('', views.index, name='list'),
    path('update_task/<str:pk>/', views.updateTask, name='updateTask'),
    path('delete/<str:pk>/', views.deleteTask, name='delete'),
]

