"""Accounts app serializers."""

from rest_framework import serializers
from .models import UserProfile, UserFollow


class UserProfileSerializer(serializers.ModelSerializer):
    """Read/write user profile data."""

    class Meta:
        model = UserProfile
        fields = [
            "id", "keycloak_sub", "display_name", "avatar_url", "bio",
            "language", "timezone", "role", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "keycloak_sub", "role", "is_active", "created_at", "updated_at"]


class PublicProfileSerializer(serializers.ModelSerializer):
    """Public profile — minimal info for social display."""

    class Meta:
        model = UserProfile
        fields = ["id", "display_name", "avatar_url", "bio", "role", "created_at"]


class FollowersSerializer(serializers.ModelSerializer):
    """Serializer for followers list — shows follower profile."""
    follower = PublicProfileSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = ["id", "follower", "created_at"]


class FollowingSerializer(serializers.ModelSerializer):
    """Serializer for following list — shows following profile."""
    following = PublicProfileSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = ["id", "following", "created_at"]