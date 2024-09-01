import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(f"Exception caught in CustomErrorMiddleware: {e}", exc_info=True)
            context = {'error_message': str(e)}
            logger.info(f"Rendering error.html with context: {context}")
            return render(request, 'error.html', context, status=500)
        return response

