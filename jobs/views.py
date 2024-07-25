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


def jobsearch_detail(request, job_search_id):
    """A view to show job search details"""

    jobsearch = get_object_or_404(Jobsearch, pk=job_search_id)

    context = {
        "jobsearch": jobsearch,
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



def edit_jobsearch(request, jobsearch_id):
    """Edit a plant in the store"""
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("display_data"))
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES, instance=jobsearch)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated jobsearch!")
            return redirect(reverse("jobsearch_detail", args=[jobsearch.id]))
        else:
            messages.error(
                request,
                "Failed to update jobsearch. Please ensure the form is valid.",
            )
    else:
        form = JobsearchForm(instance=jobsearch)
        messages.info(request, f"You are editing {jobsearch.organisation}")

    template = "jobs/edit_jobsearch.html"
    context = {
        "form": form,
        "jobsearch": jobsearch,
    }

    return render(request, template, context)
