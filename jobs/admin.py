from django.contrib import admin
from .models import Jobsearch


class JobsearchAdmin(admin.ModelAdmin):
    list_display = (
         "created_at",
         "organisation",
            )

admin.site.register(Jobsearch)



# Register your models here.
