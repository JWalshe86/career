from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from datetime import date
from .models import Jobsearch, Lkdata
from .forms import JobsearchForm, DateForm, LkdataForm

import plotly.express as px


@login_required
def jobs_searched(request):
    if request.user.is_superuser:
        """display jobs searched data"""
        jobs = Jobsearch.objects.all().order_by('response').values()
        jobs = jobs.annotate(
         priority1=Q(response='offer'),
         priority2=Q(response='interview'),
         priority3=Q(response='pre_int_screen'),
         priority4=Q(response='pending'),
         priority5=Q(response='not_proceeding'),
         )

        jobs = jobs.order_by("-priority1", "-priority2", "-priority3", "-priority4") 
        
        context = {
            "jobs_searched": jobs,
                } 
        return render(request, "jobs/job_searches.html",context)

@login_required
def jobsearch_detail(request, jobsearch_id):
        if request.user.is_superuser:
            """A view to show job search details"""

        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)

        context = {
            "jobsearch": jobsearch,
        }
        return render(request, "jobs/jobsearch_detail.html", context)


@login_required
def add_jobsearch(request):
    if request.user.is_superuser:
        "add data from google sheet"
        if request.method == "POST":
            form = JobsearchForm(request.POST, request.FILES)
            if form.is_valid():
                jobs = Jobsearch.objects.all()
                x = request.POST
                today = date.today()
                count = []
                for i in jobs:
                
                    # Alerts if already applied for a role
                    if i.name == x['name'] and i.role == x['role']:
                        messages.warning(request, f"You've already applied for this job on {i.created_at}!")
                        return redirect(reverse('add_jobsearch'))

                    # Alerts if you've applied for 10 jobs in a day
                    if i.created_at == today:
                        count.append(1)

                if len(count) == 10:
                     messages.warning(request, f"Today: {today} you've applied for {len(count)} jobs!")

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


@login_required
def edit_jobsearch(request, jobsearch_id):
    if request.user.is_superuser:
        """Edit a plant in the store"""
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
            messages.info(request, f"You are editing {jobsearch.name}")

        template = "jobs/edit_jobsearch.html"
        context = {
            "form": form,
            "jobsearch": jobsearch,
        }

        return render(request, template, context)

@login_required
def delete_jobsearch(request, jobsearch_id):
    if request.user.is_superuser:
        """Delete a jobsearch"""
        jobsearch = get_object_or_404(Jobsearch, pk=jobsearch_id)
        jobsearch.delete()
        messages.success(request, "Jobsearch deleted!")
        return redirect(reverse("jobs_searched"))



@login_required
def jobsdb(request):
    """Display jobs dashboard"""
    return render(request,"jobs/jobsdb.html")


# Data entry views start


def display_lkdata(request):
    lkdata = Lkdata.objects.values()
    x_data = []
    y_data = []
    q_data = []
    r_data = []
    z_data = []
    w_data = []
    s_data = []
    t_data = []
    m_data = []
    n_data = []
    for i in lkdata:
        y_data.append(i['impressions'])
        x_data.append(i['date'])
        q_data.append(i['srch_appears'])
        r_data.append(i['date'])
        z_data.append(i['uni_views'])
        w_data.append(i['date'])
        s_data.append(i['engagements'])
        t_data.append(i['date'])
        m_data.append(i['followers'])
        n_data.append(i['date'])
   
    imp_data = px.line(x=x_data, y=y_data, title="Impressions over past week") 
    srch_data = px.line(x=q_data, y=r_data, title="Searches over past week") 
    uni_data = px.line(x=z_data, y=w_data, title="Unique views over week") 
    engagements_data = px.line(x=s_data, y=t_data, title="Engagements over week") 
    followers_data = px.line(x=m_data, y=n_data, title="Followers over week") 
  
    impressions = imp_data.to_html()
    srch_appears = srch_data.to_html()
    uni_views = uni_data.to_html()
    engagements = engagements_data.to_html()
    followers = followers_data.to_html()
    
    return render(request, "jobs/jobs_dashboard.html", context={'impressions': impressions,
        'srch_appears': srch_appears, 'uni_views': uni_views, 'engagements': engagements, 'followers': followers })



def add_lkdata(request):
	if request.method == "POST":
		form = LkdataForm(request.POST, request.FILES)
		if form.is_valid():
			lkdata = Lkdata.objects.all()
			data = form.save()
			messages.success(request, "Successfully added linkedin data!")
			return redirect(reverse("display_lkdata"))

	else:
		form = LkdataForm()

	template = "add_lkdata.html"

	context = {
		"form" :form,
			}


	return render(request, template, context)


