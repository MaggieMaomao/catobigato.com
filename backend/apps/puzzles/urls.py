"""Puzzles app URL routing."""

from django.urls import path
from . import views

app_name = "puzzles"

urlpatterns = [
    path("puzzles/", views.PuzzlesStubView.as_view(), name="puzzles-list"),
    path("sources/", views.PuzzleSourcesStubView.as_view(), name="sources-list"),
]