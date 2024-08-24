# utils.py
from django.conf import settings
from django.urls import reverse

def get_oauth_cb_url(request, cb_hostname=None):
    """
    Generate the OAuth callback URL.

    :param request: Django request object
    :param cb_hostname: Optional hostname to override the default
    :return: OAuth callback URL
    """
    if cb_hostname is None:
        cb_hostname = settings.DEFAULT_HOSTNAME
    
    callback_url = request.build_absolute_uri(
        reverse('oauth2callback')  # Adjust this to your actual OAuth callback view name
    )
    return callback_url

