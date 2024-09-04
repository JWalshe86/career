from django.db import models
from django.contrib.auth.models import User

class OAuthToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.JSONField()
    expiry = models.DateTimeField()
    
    def __str__(self):
        return f"OAuthToken for {self.user.username}"

