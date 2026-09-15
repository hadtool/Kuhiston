from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.object_list, name="object_list"),
    path("object/<int:pk>/", views.object_detail, name="object_detail"),
    path("my/", views.my_panel, name="my_panel"),
    path("my/<int:pk>/<str:status>/", views.set_status, name="set_status"),
]