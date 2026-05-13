"""Social app URL routing."""

from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    path("conversations/", views.ConversationsStubView.as_view(), name="conversations"),
    path("messages/", views.MessagesStubView.as_view(), name="messages"),
]