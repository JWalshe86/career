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
    

    name = models.CharField(max_length=127)
    zipcode = models.CharField(max_length=200,blank=True, null=True)
    city = models.CharField(max_length=127)
    country = models.CharField(max_length=200,blank=True, null=True)
    address = models.CharField(max_length=200,blank=True, null=True)
    tech = models.CharField(max_length=127, null=True, blank=True)
    role = models.CharField(blank=True, default=None, max_length=127, null=True)
    text_used = models.TextField(null=True, blank=True)
    method = models.CharField(blank=True, choices=METHOD_CHOICES, default='lkeasy', max_length=127, null=True)
    status = models.CharField(blank=True, choices=RESPONSE_CHOICES, default='pending', max_length=127, null=True)
    search_imgs = models.ImageField(blank=True, upload_to='static/images/%Y/%m/%d')
    docfile = models.FileField(blank=True, upload_to='static/documents/%Y/%m/%d')
    created_at = models.DateField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    lat = models.CharField(max_length=200,blank=True, null=True)
    lng = models.CharField(max_length=200,blank=True, null=True)
    place_id = models.CharField(max_length=200,blank=True, null=True)



    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f'{self.name} {self.created_at}'




class Lkdata(models.Model):
    date = models.DateField()
    impressions = models.IntegerField(blank=True, null=True)
    srch_appears = models.IntegerField(blank=True, null=True)
    uni_views = models.IntegerField(blank=True, null=True)
    engagements = models.IntegerField(blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('date',)


    

