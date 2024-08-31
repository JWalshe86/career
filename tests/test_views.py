# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from google.auth.exceptions import GoogleAuthError

class OAuth2CallbackErrorTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.error_url = reverse('error_view')

    @patch('jobs.views.flow.fetch_token')
    def test_oauth2_callback_redirects_to_error_page(self, mock_fetch_token):
        # Simulate an OAuth error
        mock_fetch_token.side_effect = GoogleAuthError("redirect_uri_mismatch")

        response = self.client.get(reverse('oauth2callback'))
        
        # Check if the response redirects to the error page
        self.assertRedirects(response, self.error_url)
        
        # Ensure the error page is rendered correctly
        error_response = self.client.get(self.error_url)
        self.assertEqual(error_response.status_code, 200)
        self.assertTemplateUsed(error_response, 'error.html')

