from django.shortcuts import render
from django.http import HttpResponse

def all_user(request):
    return HttpResponse('Returning all user')

# Create your views here.
