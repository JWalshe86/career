from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponseServerError
from yourapp.middleware.custom_error_middleware import CustomErrorMiddleware
import logging

class CustomErrorMiddlewareTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('test_error_view')  # Ensure this URL is defined in your urls.py

    def test_custom_error_middleware(self):
        # Simulate an error by making a request to a view that raises an exception
        response = self.client.get(self.url)

        # Check that the response is rendered with the custom error template
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, 'custom_error.html')
        self.assertContains(response, "Simulated Error Message")

