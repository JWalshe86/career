from django import forms
from .models import Jobsearch, Lkdata


class JobsearchForm(forms.ModelForm):

    class Meta:
        model = Jobsearch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(JobsearchForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:  # New instance, set default value for status
            self.fields['status'].initial = 'pending<wk'


class DateForm(forms.Form):
    start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class LkdataForm(forms.ModelForm):

    class Meta:
        model = Lkdata
        fields = "__all__"
