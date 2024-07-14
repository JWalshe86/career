from django.shortcuts import render
from . import run


def display_data(request):
    """display job search data"""
    data = run.data
    
    context = {
        "display_data": data,
            } 
    return render(request, "jobs/job_searches.html",context)


