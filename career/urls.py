from django.views.generic.base import TemplateView
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from oauth.views import oauth2callback

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('emails/', include('emails.urls')),
    path('jobs/', include('jobs.urls')),
    path('', include('oauth.urls')),
    path('users/', include('users.urls')),
    path('map/', include('map.urls')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
]
