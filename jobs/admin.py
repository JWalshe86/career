from django.contrib import admin
from .models import Jobsearch, Lkdata


class JobsearchAdmin(admin.ModelAdmin):
    list_display = (
         "created_at",
         "organisation",
            )
class LkdataAdmin(admin.ModelAdmin):
    list_display = (
         "date",
            )

admin.site.register(Jobsearch)
admin.site.register(Lkdata)



# Register your models here.
