from django.urls import path

from . import views

urlpatterns = [
        # ex: /polls/
          path("display_data", views.display_data, name="display_data"),
          path("add_data", views.add_data, name="add_data"),
        ]
