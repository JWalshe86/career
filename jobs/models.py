from django.db import models
    

METHOD_CHOICES = (
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


class Jobsearch(models.Model):
    

    organisation = models.CharField(max_length=127)
    type = models.CharField(blank=True, choices=TYPE_CHOICES, default='private', max_length=127, null=True)
    location = models.CharField(max_length=127)
    url = models.URLField(max_length=300, null=True, blank=True)
    contact = models.CharField(max_length=127, null=True, blank=True, default=None)
    role = models.CharField(blank=True, default=None, max_length=127, null=True)
    text_used = models.TextField()
    method = models.CharField(blank=True, choices=METHOD_CHOICES, default='lkpsearch', max_length=127, null=True)
    response = models.CharField(max_length=127, null=True, blank=True, default=None)
    search_imgs = models.ImageField(blank=True, upload_to='static/images/%Y/%m/%d')
    docfile = models.FileField(blank=True, upload_to='static/documents/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.organisation} {self.created_at}'

