from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, redirect
from .models import *
from jobs.models import Jobsearch, Lkdata
import googlemaps
from django.conf import settings
from .forms import *
from datetime import datetime
import plotly.express as px


class HomeView(ListView):
    template_name = "map/home.html"
    context_object_name = 'mydata'
    model = Jobsearch
    success_url = "/"

class MapView(View): 
    template_name = "map/map.html"

    def get(self,request): 
        # lkdata = Lkdata.objects.values()
        # x_data = []
        # y_data = []
        # for i in lkdata:
        #     y_data.append(i['impressions'])
        #     x_data.append(i['date'])
        # imp_data = px.line(x=x_data, y=y_data, title="Impressions over past week")
        # impressions = imp_data.to_html()

        key = settings.GOOGLE_API_KEY
        eligable_locations = Jobsearch.objects.filter(place_id__isnull=False)
        locations = []

        for a in eligable_locations: 
            data = {
                'lat': float(a.lat), 
                'lng': float(a.lng), 
                'name': a.name
            }

            locations.append(data)


        context = {
            "key":key, 
            "locations": locations,
            # "impressions": impressions,
        }

        return render(request, self.template_name, context)

class DistanceView(View):
    template_name = "map/distance.html"

    def get(self, request): 
        form = DistanceForm
        distances = Distances.objects.all()
        context = {
            'form':form,
            'distances':distances
        }

        return render(request, self.template_name, context)

    def post(self, request): 
        form = DistanceForm(request.POST)
        if form.is_valid(): 
            from_location = form.cleaned_data['from_location']
            from_location_info = Jobsearch.objects.get(name=from_location)
            from_address_string = str(from_location_info.address)+", "+str(from_location_info.zipcode)+", "+str(from_location_info.city)+", "+str(from_location_info.country)

            to_location = form.cleaned_data['to_location']
            to_location_info = Jobsearch.objects.get(name=to_location)
            to_address_string = str(to_location_info.address)+", "+str(to_location_info.zipcode)+", "+str(to_location_info.city)+", "+str(to_location_info.country)

            mode = form.cleaned_data['mode']
            now = datetime.now()

            gmaps = googlemaps.Client(key= settings.GOOGLE_API_KEY)
            calculate = gmaps.distance_matrix(
                    from_address_string,
                    to_address_string,
                    mode = mode,
                    departure_time = now
            )


            duration_seconds = calculate['rows'][0]['elements'][0]['duration']['value']
            duration_minutes = duration_seconds/60

            distance_meters = calculate['rows'][0]['elements'][0]['distance']['value']
            distance_kilometers = distance_meters/1000

            if 'duration_in_traffic' in calculate['rows'][0]['elements'][0]: 
                duration_in_traffic_seconds = calculate['rows'][0]['elements'][0]['duration_in_traffic']['value']
                duration_in_traffic_minutes = duration_in_traffic_seconds/60
            else: 
                duration_in_traffic_minutes = None

            
            obj = Distances(
                from_location = Jobsearch.objects.get(name=from_location),
                to_location = Jobsearch.objects.get(name=to_location),
                mode = mode,
                distance_km = distance_kilometers,
                duration_mins = duration_minutes,
                duration_traffic_mins = duration_in_traffic_minutes
            )

            obj.save()

        else: 
            print(form.errors)
        
        return redirect('my_distance_view')


class GeocodingView(View):
    template_name = "map/geocoding.html"

    def get(self,request,pk): 
        location = Jobsearch.objects.get(pk=pk)

        if location.lng and location.lat and location.place_id != None: 
            lat = location.lat
            lng = location.lng
            place_id = location.place_id
            label = "from my database"

        elif location.address and location.country and location.zipcode and location.city != None: 
            address_string = str(location.address)+", "+str(location.zipcode)+", "+str(location.city)+", "+str(location.country)

            gmaps = googlemaps.Client(key = settings.GOOGLE_API_KEY)
            result = gmaps.geocode(address_string)[0]
            
            lat = result.get('geometry', {}).get('location', {}).get('lat', None)
            lng = result.get('geometry', {}).get('location', {}).get('lng', None)
            place_id = result.get('place_id', {})
            label = "from my api call"

            location.lat = lat
            location.lng = lng
            location.place_id = place_id
            location.save()

        else: 
            result = ""
            lat = ""
            lng = ""
            place_id = ""
            label = "no call made"

        context = {
            'location':location,
            'lat':lat, 
            'lng':lng, 
            'place_id':place_id, 
            'label': label
        }
        
        return render(request, self.template_name, context)

