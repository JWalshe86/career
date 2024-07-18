from django.db import models

class Jobsearch(models.Model):

    organisation = models.CharField(max_length=127)
    url = models.URLField(max_length=300)
    contact = models.CharField(max_length=127, null=True, blank=True, default=None)
    role = models.CharField(blank=True, default=None, max_length=127, null=True)
    text_used = models.TextField()
    method = models.CharField(max_length=127, null=True, blank=True, default=None)
    response = models.CharField(blank=True, default=None, max_length=127, null=True)
    search_imgs = models.ImageField(blank=True, upload_to=None)
    docfile = models.FileField(blank=True, upload_to='documents/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.organisation} {self.created_at}'

