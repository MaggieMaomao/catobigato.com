"""Accounts schemas — Pydantic request/response models."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


class UserProfileBase(BaseModel):
    display_name: str = ""
    bio: str = ""
    language: str = "en"
    timezone: str = "America/Toronto"
    role: str = "student"


class UserProfileCreate(UserProfileBase):
    keycloak_sub: uuid.UUID


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    id: uuid.UUID
    keycloak_sub: uuid.UUID
    avatar_url: str = ""
    is_active: bool = True
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class FollowRequest(BaseModel):
    target_user_id: uuid.UUID


class FollowResponse(BaseModel):
    ok: bool
    following_id: uuid.UUID


class UserStats(BaseModel):
    followers_count: int = 0
    following_count: int = 0
    notes_count: int = 0
    questions_count: int = 0


class CurrentUserResponse(BaseModel):
    """Current user derived from Keycloak JWT."""
    sub: str
    username: str
    email: str
    display_name: str
    first_name: str = ""
    last_name: str = ""
    roles: list[str] = []
    is_admin: bool = False
    language: str = "en"
    timezone: str = "America/Toronto"