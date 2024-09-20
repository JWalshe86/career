app_name = 'oauth'

from django.urls import path
from .views import oauth_login, oauth_callback, env_vars

urlpatterns = [
    path('oauth-start/', oauth_login, name='oauth_login'),
    path('callback/', oauth_callback, name='oauth_callback'),
    path('env_vars/', env_vars, name='env_vars'),  # Add this line
]

