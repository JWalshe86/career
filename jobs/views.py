from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from .models import Jobsearch
from .forms import JobsearchForm


def jobs_searched(request):
    """display jobs searched data"""
    jobs = Jobsearch.objects.all().order_by('response').values()
    jobs = jobs.annotate(
     priority1=Q(response='not_proceeding'),
     )

    jobs = jobs.order_by("priority1") 
    
    context = {
        "jobs_searched": jobs,
            } 
    return render(request, "jobs/job_searches.html",context)


def jobsearch_detail(request, jobsearch_id):
    """A view to show job search details"""

    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)

    context = {
        "jobsearch": jobsearch,
    }
    return render(request, "jobs/jobsearch_detail.html", context)



def add_jobsearch(request):
    "add data from google sheet"
    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            messages.success(request, "Successfully added job application!")
            return redirect(reverse("jobs_searched"))

    else:
        form = JobsearchForm()

    template = "jobs/add_jobsearch.html"

    context = {
        "form" :form,
            }


    return render(request, template, context)



def edit_jobsearch(request, jobsearch_id):
    """Edit a plant in the store"""
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("jobs_searched"))
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    if request.method == "POST":
        form = JobsearchForm(request.POST, request.FILES, instance=jobsearch)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated jobsearch!")
            return redirect(reverse("jobs_searched"))
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


def delete_jobsearch(request, jobsearch_id):
    """Delete a jobsearch"""
    jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
    jobsearch.delete()
    messages.success(request, "Jobsearch deleted!")
    return redirect(reverse("jobs_searched"))





