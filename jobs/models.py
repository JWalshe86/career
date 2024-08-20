from django.db import models
from django.db.models import Case, When, Value
    

METHOD_CHOICES = (
    ('cislack', 'CISLACK'),
    ('dm', 'DM'),
    ('indeed', 'INDEED'),
    ('lkeasy', 'LKEASY'),
    ('lkpsearch', 'LKPSearch'),
    ('jobs.ie', 'JOBS.IE'),
    ('lkjobsug', 'LKJOBSUG'),
    ('inform', 'INFORM'),
    ('irishjobs.ie', 'IRISHJOBS.IE'),
            )

TYPE_CHOICES = (
    ('private', 'PRIVATE'),
    ('public', 'PUBLIC'),
    ('local', 'LOCAL'),
            )

EIRCODE_CHOICES = (
    ('DO2 PN40', 'DO2 PN40'),
    ('H91 E2R8', 'H91 E2R8'),
    ('T23 E6TD', 'T23 E6TD'),
    ('C15 H04P', 'C15 H04P'),
            )


STATUS_CHOICES = (
    ('not_proceeding', 'NOT_PROCEEDING'),
    ('pre_int_screen', 'PRE_INT_SCREEN'),
    ('interview', 'INTERVIEW'),
    ('offer', 'OFFER'),
    ('appinprog', 'APPINPROG'),
    ('pending<wk', 'PENDING<WK'),
    ('pending<2wk', 'PENDING<2WK'),
    ('pend<MONTH', 'PEND<MONTH'),
    ('pend+month', 'PEND+MONTH'),
            )


class Jobsearch(models.Model):
    

    favourite = models.BooleanField(default=False)
    name = models.CharField(max_length=127)
    eircode = models.CharField(choices=EIRCODE_CHOICES, max_length=200,blank=True, null=True, default='DO2 PN40')
    city = models.CharField(max_length=127, default='Dublin')
    country = models.CharField(max_length=200,blank=True, null=True, default='Ireland')
    address = models.CharField(max_length=200,blank=True, null=True)
    tech = models.CharField(max_length=127, null=True, blank=True)
    role = models.CharField(blank=True, default=None, max_length=127, null=True)
    text_used = models.TextField(null=True, blank=True)
    method = models.CharField(blank=True, choices=METHOD_CHOICES, default='dm', max_length=127, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='pending<wk', max_length=127, null=True)
    search_imgs = models.ImageField(blank=True, upload_to='static/images/%Y/%m/%d')
    docfile = models.FileField(blank=True, upload_to='static/documents/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)
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


    

