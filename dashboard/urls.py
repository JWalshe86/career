from django.urls import path
from .views import dashboard_basic, dashboard_searched

urlpatterns = [
    path('basic/', dashboard_basic, name='dashboard_basic'),
    path('searched/', dashboard_searched, name='dashboard_searched'),
]

