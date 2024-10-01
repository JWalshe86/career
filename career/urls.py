from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from dashboard import views as error_views

urlpatterns = [
    # Homepage URL
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # Admin interface
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # Emails app
    path('emails/', include('emails.urls')),

    # Jobs app
    path('jobs/', include('jobs.urls')),

    # OAuth URLs
    path('oauth/', include('oauth.urls')),

    # Users app
    path('users/', include('users.urls')),

    # Map app
    path('map/', include('map.urls')),

    # Tasks app
    path('tasks/', include('tasks.urls', namespace='tasks')),

    # Dashboard app
    path('dashboard/', include('dashboard.urls')),
    
    path('error/', error_views.error_view, name='error_view'),  # Add this line
    ]
