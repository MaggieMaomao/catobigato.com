"""Social router stub — conversations and messages."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, CurrentUser

router = APIRouter(prefix="/social", tags=["social"])

# Conversations and messages — stub will be implemented in Step 4 of migration

@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    # TODO: implement
    return []


@router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    # TODO: implement
    return []