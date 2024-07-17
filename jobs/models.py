from django.db import models

class Jobsearch(models.Model):

    organistion = models.CharField(max_length=127)
    url = models.URLField(max_length=300)
    contact = models.CharField(max_length=127, null=True, blank=True, default=None)
    role = models.CharField(max_length=127, null=True, blank=True, default=None)
    text_used = models.TextField()
    method = models.CharField(max_length=127, null=True, blank=True, default=None)
    response = models.CharField(max_length=127, null=True, blank=True, default=None)
    search_imgs = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

