"""User profile models — extends Keycloak users."""

import uuid
from django.db import models


class UserProfile(models.Model):
    """
    Extended user profile for CatobiGato.
    The primary identity (sub) comes from Keycloak.
    This model stores additional profile information.
    """

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("zh", "Chinese"),
        ("fr", "French"),
    ]

    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("creator", "Content Creator"),
        ("admin", "Administrator"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Keycloak subject (sub) — links to Keycloak identity
    keycloak_sub = models.UUIDField(unique=True, db_index=True)

    # Profile info
    display_name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    bio = models.TextField(blank=True, max_length=500)

    # Preferences
    language = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="en"
    )
    timezone = models.CharField(max_length=50, default="America/Toronto")

    # Role-based access
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="student"
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.display_name or self.keycloak_sub} ({self.role})"


class UserFollow(models.Model):
    """Follow relationship between users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="following_set",
    )
    following = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="follower_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_follows"
        unique_together = ("follower", "following")
        verbose_name = "User Follow"
        verbose_name_plural = "User Follows"

    def __str__(self):
        return f"{self.follower} follows {self.following}"