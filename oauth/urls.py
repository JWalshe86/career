from django.urls import path
from .views import oauth_login, oauth_callback_view

urlpatterns = [
    path('login/', oauth_login, name='oauth_login'),
    path('oauth/callback/', oauth_callback_view, name='oauth_callback'),
]

