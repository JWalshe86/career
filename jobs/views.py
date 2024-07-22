from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Jobsearch
from .forms import JobsearchForm


def display_data(request):
    """display job search data"""
    jobs = Jobsearch.objects.all()
    
    context = {
        "display_data": jobs,
            } 
    return render(request, "jobs/job_searches.html",context)


def job_search_detail(request, job_search_id):
    """A view to show job search details"""

    jobdetail = get_object_or_404(Jobsearch, pk=job_search_id)

    context = {
        "jobdetail": jobdetail,
    }
    return render(request, "jobs/job_search_detail.html", context)



def add_data(request):
    "add data from google sheet"
    if request.method == "POST":
        print('in add_data')
        form = JobsearchForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            messages.success(request, "Successfully added job application!")
            return redirect(reverse("display_data"))

    else:
        form = JobsearchForm()

    template = "jobs/add_data.html"

    context = {
        "form" :form,
            }


    return render(request, template, context)
