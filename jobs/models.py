from django.db import models

class Jobsearch(models.Model):

    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    email = models.CharField(max_length=127, null=True, blank=True, default=None)
    phone = models.CharField(max_length=127, null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

