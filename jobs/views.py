from django.shortcuts import render
from .models import Jobsearch
from .forms import JobsearchForm


def display_data(request):
    """display job search data"""
    jobs = Jobsearch.objects.all()
    
    context = {
        "display_data": jobs,
            } 
    return render(request, "jobs/job_searches.html",context)


def add_data(request):
    "add data from google sheet"
    if request.method == "POST":
        print('in add_data')
        form = JobsearchForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()

    else:
        form = JobsearchForm()

    template = "jobs/add_data.html"

    context = {
        "form" :form,
            }


    return render(request, template, context)
