"""Accounts API router — profile + follow."""

import uuid as uuid_lib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.models.accounts import UserProfile, UserFollow
from pydantic import BaseModel

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    language: str | None = None
    timezone: str | None = None


class ProfileResponse(BaseModel):
    id: str
    display_name: str
    bio: str
    avatar_url: str | None
    language: str
    timezone: str
    role: str
    is_active: bool


class FollowResponse(BaseModel):
    following: bool


def _parse_uuid(val: str) -> uuid_lib.UUID | None:
    try:
        return uuid_lib.UUID(val)
    except (ValueError, AttributeError):
        return None


# Helper: get or create user profile from Keycloak token
async def get_or_create_profile(db: AsyncSession, user: CurrentUser) -> UserProfile:
    # keycloak_sub is stored as UUID in the DB
    sub_uuid = _parse_uuid(user.sub)
    if sub_uuid:
        stmt = select(UserProfile).where(UserProfile.keycloak_sub == sub_uuid)
    else:
        # Fallback: store sub as string if not UUID
        stmt = select(UserProfile).where(UserProfile.keycloak_sub == user.sub)

    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(
            keycloak_sub=sub_uuid or user.sub,  # uuid if valid, else store string
            display_name=user.name or user.email or "User",
            language=user.locale or "en",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.get("/me", response_model=ProfileResponse)
async def get_me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await get_or_create_profile(db, user)
    return ProfileResponse(
        id=str(profile.id),
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        language=profile.language,
        timezone=profile.timezone,
        role=profile.role,
        is_active=profile.is_active,
    )


@router.put("/me", response_model=ProfileResponse)
async def update_me(data: ProfileUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await get_or_create_profile(db, user)
    if data.display_name is not None:
        profile.display_name = data.display_name
    if data.bio is not None:
        profile.bio = data.bio
    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url
    if data.language is not None:
        profile.language = data.language
    if data.timezone is not None:
        profile.timezone = data.timezone
    await db.commit()
    await db.refresh(profile)
    return ProfileResponse(
        id=str(profile.id),
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        language=profile.language,
        timezone=profile.timezone,
        role=profile.role,
        is_active=profile.is_active,
    )


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_public_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(UserProfile).where(UserProfile.id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileResponse(
        id=str(profile.id),
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        language=profile.language,
        timezone=profile.timezone,
        role=profile.role,
        is_active=profile.is_active,
    )


@router.post("/follow/{user_id}", response_model=FollowResponse)
async def follow_user(user_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    my_profile = await get_or_create_profile(db, user)

    stmt = select(UserProfile).where(UserProfile.id == user_id)
    result = await db.execute(stmt)
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    stmt2 = select(UserFollow).where(
        UserFollow.follower_id == my_profile.id,
        UserFollow.following_id == target.id,
    )
    existing = await db.execute(stmt2)
    if existing.scalar_one_or_none():
        return FollowResponse(following=True)

    follow = UserFollow(follower_id=my_profile.id, following_id=target.id)
    db.add(follow)
    await db.commit()
    return FollowResponse(following=True)


@router.delete("/follow/{user_id}", response_model=FollowResponse)
async def unfollow_user(user_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    my_profile = await get_or_create_profile(db, user)

    stmt = select(UserProfile).where(UserProfile.id == user_id)
    result = await db.execute(stmt)
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    stmt2 = select(UserFollow).where(
        UserFollow.follower_id == my_profile.id,
        UserFollow.following_id == target.id,
    )
    result2 = await db.execute(stmt2)
    follow = result2.scalar_one_or_none()
    if follow:
        await db.delete(follow)
        await db.commit()

    return FollowResponse(following=False)


@router.get("/followers/")
async def list_followers(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    my_profile = await get_or_create_profile(db, user)
    stmt = select(UserFollow).where(UserFollow.following_id == my_profile.id)
    result = await db.execute(stmt)
    follows = result.scalars().all()
    return [{"user_id": str(f.follower_id), "followed_at": f.created_at.isoformat()} for f in follows]


@router.get("/following/")
async def list_following(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    my_profile = await get_or_create_profile(db, user)
    stmt = select(UserFollow).where(UserFollow.follower_id == my_profile.id)
    result = await db.execute(stmt)
    follows = result.scalars().all()
    return [{"user_id": str(f.following_id), "followed_at": f.created_at.isoformat()} for f in follows]
