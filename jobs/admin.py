from django.contrib import admin
from .models import Jobsearch


class JobsearchAdmin(admin.ModelAdmin):
    list_display = (
         "first_name",
         "last_name",
            )

admin.site.register(Jobsearch)



# Register your models here.
