class SimpleTestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            return HttpResponse(f"Middleware caught an error: {e}", status=500)
        return response

