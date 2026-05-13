"""Learning app URL routing."""

from django.urls import path, include
from . import views

app_name = "learning"

urlpatterns = [
    # Stub endpoints — real implementation in Phase 2
    path("notes/", views.NotesStubView.as_view(), name="notes-list"),
    path("questions/", views.QuestionsStubView.as_view(), name="questions-list"),
    path("question-sets/", views.QuestionSetsStubView.as_view(), name="question-sets-list"),
    path("exams/", views.ExamsStubView.as_view(), name="exams-list"),
]