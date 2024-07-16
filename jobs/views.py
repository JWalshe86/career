from django.shortcuts import render
from . import run
from .forms import JobsearchForm


def display_data(request):
    """display job search data"""
    data = run.data
    
    context = {
        "display_data": data,
            } 
    return render(request, "jobs/job_searches.html",context)


def add_data(request):
    "add data from google sheet"
    if request.method == "POST":
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
