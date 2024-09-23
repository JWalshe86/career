from django.contrib import admin
from .models import OAuthToken

@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'refresh_token', 'expiry')  # Add any fields you want to display


