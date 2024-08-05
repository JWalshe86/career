from django.db import models
from django.db.models import Case, When, Value
    

METHOD_CHOICES = (
    ('lkeasy', 'LKEASY'),
    ('lkpsearch', 'LKPSearch'),
    ('cislack', 'CISLACK'),
    ('lkjobsug', 'LKJOBSUG'),
    ('inform', 'INFORM'),
    ('irishjobs.ie', 'IRISHJOBS.IE'),
            )

TYPE_CHOICES = (
    ('private', 'PRIVATE'),
    ('public', 'PUBLIC'),
    ('local', 'LOCAL'),
            )


RESPONSE_CHOICES = (
    ('pending', 'PENDING'),
    ('pending1mnt', 'PENDING1MNT'),
    ('not_proceeding', 'NOT_PROCEEDING'),
    ('pre_int_screen', 'PRE_INT_SCREEN'),
    ('interview', 'INTERVIEW'),
    ('offer', 'OFFER'),
            )


class Jobsearch(models.Model):
    

    organisation = models.CharField(max_length=127)
    tech = models.CharField(max_length=127, null=True, blank=True)
    location = models.CharField(max_length=127)
    url = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(blank=True, default=None, max_length=127, null=True)
    text_used = models.TextField(null=True, blank=True)
    method = models.CharField(blank=True, choices=METHOD_CHOICES, default='lkeasy', max_length=127, null=True)
    response = models.CharField(blank=True, choices=RESPONSE_CHOICES, default='pending', max_length=127, null=True)
    search_imgs = models.ImageField(blank=True, upload_to='static/images/%Y/%m/%d')
    docfile = models.FileField(blank=True, upload_to='static/documents/%Y/%m/%d')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f'{self.organisation} {self.created_at}'


class Lkdata(models.Model):
    date = models.DateField()
    average = models.FloatField()

    class Meta:
        ordering = ('date',)


    

