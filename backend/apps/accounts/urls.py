"""Accounts app URL routing."""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Profile
    path("profile/", views.OwnProfileView.as_view(), name="own-profile"),
    path("profile/<uuid:user_id>/", views.PublicProfileView.as_view(), name="public-profile"),

    # Follow/Unfollow
    path("follow/<uuid:user_id>/", views.FollowUserView.as_view(), name="follow-user"),
    path("followers/", views.FollowersListView.as_view(), name="followers"),
    path("following/", views.FollowingListView.as_view(), name="following"),
    path("follow-status/<uuid:user_id>/", views.CheckFollowStatusView.as_view(), name="follow-status"),
]