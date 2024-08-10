from django import forms
from .models import Jobsearch, Lkdata


class JobsearchForm(forms.ModelForm):

    class Meta:
        model = Jobsearch
        fields = "__all__"


class DateForm(forms.Form):
    start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class LkdataForm(forms.ModelForm):

    class Meta:
        model = Lkdata
        fields = "__all__"
