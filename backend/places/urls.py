from django.urls import path

from . import views

app_name = "places"

urlpatterns = [
    path("volunteer/places/add/", views.volunteer_place_add, name="volunteer_place_add"),
]
