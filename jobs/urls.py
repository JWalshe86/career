from django.urls import path

from . import views

urlpatterns = [
        # ex: /polls/
          path("display_data", views.display_data, name="display_data"),
        ]
