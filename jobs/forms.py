from django import forms
from .models import Jobsearch


class JobsearchForm(forms.ModelForm):

    class Meta:
        model = Jobsearch
        fields = "__all__"

