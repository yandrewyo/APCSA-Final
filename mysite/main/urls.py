from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("swimmerPage/", views.swimmerPage, name="swimmerPage"),
    path("swimmerPage/event/", views.event, name="eventPage"),
]
