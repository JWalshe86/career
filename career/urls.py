from django.views.generic.base import TemplateView
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from jobs.views import error_view, oauth2callback, trigger_middleware_error

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('jobs/', include('jobs.urls')),
    path('users/', include('users.urls')),
    path('map/', include('map.urls')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path("trigger-error/", trigger_middleware_error, name="trigger_middleware_error"),  # OAuth2 callback view
    path("error/", error_view, name="error_view"),  # OAuth2 callback view
    path("oauth2callback/", oauth2callback, name="oauth2callback"),
]
