"""Accounts app views — profile CRUD and social (follow/unfollow)."""

from django.db.models import Q
from rest_framework import generics, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .authentication import KeycloakAuthentication
from .models import UserFollow, UserProfile
from .serializers import (
    FollowersSerializer,
    FollowingSerializer,
    PublicProfileSerializer,
    UserProfileSerializer,
)


# ── Profile ──────────────────────────────────────────────────────────────────


class OwnProfileView(views.APIView):
    """
    GET  /accounts/profile/         → current user's profile
    PUT  /accounts/profile/          → update current user's profile
    PATCH /accounts/profile/         → partial update
    """
    authentication_classes = [KeycloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            keycloak_sub=request.user.sub,
            defaults={
                "display_name": request.user.display_name,
                "email": request.user.email,
            }
        )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            keycloak_sub=request.user.sub,
            defaults={
                "display_name": request.user.display_name,
                "email": request.user.email,
            }
        )
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicProfileView(generics.RetrieveAPIView):
    """
    GET /accounts/profile/<uuid>/  → any user's public profile
    """
    queryset = UserProfile.objects.filter(is_active=True)
    serializer_class = PublicProfileSerializer
    lookup_field = "id"


# ── Follow / Unfollow ─────────────────────────────────────────────────────────


class FollowUserView(views.APIView):
    """
    POST   /accounts/follow/<uuid>/  → follow a user
    DELETE /accounts/follow/<uuid>/  → unfollow a user
    GET    /accounts/follow/<uuid>/  → check follow status
    """
    authentication_classes = [KeycloakAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """Follow user <id>."""
        if str(request.user.sub) == str(id):
            return Response({"detail": "Cannot follow yourself"}, status=400)

        target = generics.get_object_or_404(UserProfile.objects.filter(id=id, is_active=True), id=id)
        my_profile, _ = UserProfile.objects.get_or_create(
            keycloak_sub=request.user.sub,
            defaults={"display_name": request.user.display_name, "email": request.user.email},
        )

        follow, created = UserFollow.objects.get_or_create(follower=my_profile, following=target)
        if not created:
            return Response({"detail": "Already following"}, status=200)

        return Response({"detail": "Followed"}, status=201)

    def delete(self, request, id):
        """Unfollow user <id>."""
        my_profile = UserProfile.objects.filter(keycloak_sub=request.user.sub).first()
        if not my_profile:
            return Response({"detail": "Profile not found"}, status=404)

        deleted, _ = UserFollow.objects.filter(follower=my_profile, following_id=id).delete()
        if deleted:
            return Response({"detail": "Unfollowed"}, status=200)
        return Response({"detail": "Not following"}, status=400)


class FollowersListView(generics.ListAPIView):
    """GET /accounts/followers/ → list of users who follow me."""
    authentication_classes = [KeycloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        my_profile = UserProfile.objects.filter(keycloak_sub=self.request.user.sub).first()
        if not my_profile:
            return UserProfile.objects.none()
        return UserFollow.objects.filter(following=my_profile).select_related("follower")

    serializer_class = FollowersSerializer


class FollowingListView(generics.ListAPIView):
    """GET /accounts/following/ → list of users I follow."""
    authentication_classes = [KeycloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        my_profile = UserProfile.objects.filter(keycloak_sub=self.request.user.sub).first()
        if not my_profile:
            return UserProfile.objects.none()
        return UserFollow.objects.filter(follower=my_profile).select_related("following")

    serializer_class = FollowingSerializer


class CheckFollowStatusView(views.APIView):
    """GET /accounts/follow-status/<uuid>/ → am I following this user?"""
    authentication_classes = [KeycloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        my_profile = UserProfile.objects.filter(keycloak_sub=request.user.sub).first()
        if not my_profile:
            return Response({"following": False, "followed_by": False})
        following = UserFollow.objects.filter(follower=my_profile, following_id=id).exists()
        followed_by = UserFollow.objects.filter(follower_id=id, following=my_profile).exists()
        return Response({"following": following, "followed_by": followed_by})


# ── Health check ──────────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Lightweight health check for the accounts endpoint."""
    return Response({"status": "ok", "app": "accounts"})