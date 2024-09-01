# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from google.auth.exceptions import GoogleAuthError

class OAuth2CallbackErrorTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.error_url = reverse('error_view')

    @patch('jobs.views.InstalledAppFlow.from_client_secrets_file')
    def test_oauth2_callback_redirects_to_error_page(self, mock_from_client_secrets_file):
        # Simulate an OAuth error
        mock_flow = mock_from_client_secrets_file.return_value
        mock_flow.fetch_token.side_effect = GoogleAuthError("Simulated OAuth2 error")

        response = self.client.get(reverse('oauth2callback'))
        
        # Check if the response redirects to the error page
        self.assertRedirects(response, self.error_url)
        
        # Ensure the error page is rendered correctly
        error_response = self.client.get(self.error_url)
        self.assertEqual(error_response.status_code, 200)
        self.assertTemplateUsed(error_response, 'error.html')

    def tearDown(self):
        # Clean up any modifications if necessary
        pass

