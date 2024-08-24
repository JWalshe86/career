from django.shortcuts import render
from django.views import View
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class HomeView(View):
    def get(self, request):
        return render(request, "home.html")

class GeocodingView(View):
    def get(self, request, pk):
        api_key = settings.GOOGLE_API_KEY
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={pk}&key={api_key}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            context = {"data": data}
        else:
            context = {"error": "Geocoding request failed."}
            logger.error("Geocoding request failed with status code: %s", response.status_code)
        return render(request, "geocoding.html", context)

class DistanceView(View):
    def get(self, request):
        origin = request.GET.get('origin', 'place_id=origin_place_id')
        destination = request.GET.get('destination', 'place_id=destination_place_id')
        api_key = settings.GOOGLE_API_KEY
        endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            context = {"data": data}
        else:
            context = {"error": "Distance request failed."}
            logger.error("Distance request failed with status code: %s", response.status_code)
        return render(request, "distance.html", context)

class MapView(View):
    def get(self, request):
        key = settings.GOOGLE_API_KEY
        return render(request, "map.html", {'key': key})

