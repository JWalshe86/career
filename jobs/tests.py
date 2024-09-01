from django.test import TestCase
from django.http import HttpRequest
from django.urls import reverse
from django.core.exceptions import MiddlewareNotUsed
from career.middleware.custom_error_middleware import CustomErrorMiddleware

class CustomErrorMiddlewareTest(TestCase):
    def setUp(self):
        # Initialize the middleware for testing
        self.middleware = CustomErrorMiddleware(lambda request: self.mock_view(request))
    
    def mock_view(self, request):
        # This view raises an error to be caught by the middleware
        raise RuntimeError("This is a test error")

    def test_custom_error_middleware(self):
        # Create a mock request
        request = HttpRequest()
        
        # Use the middleware to handle the request
        response = self.middleware(request)
        
        # Check if the response status code is 500 (Internal Server Error)
        self.assertEqual(response.status_code, 500)
        
        # Check if the response content contains the expected error message
        self.assertIn(b"This is a test error", response.content)

