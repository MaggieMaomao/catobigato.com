"""Puzzles router stub."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, CurrentUser
from app.models.puzzles import PuzzleSource, Puzzle

router = APIRouter(prefix="/puzzles", tags=["puzzles"])

# PuzzleSource and Puzzle CRUD stubs — same pattern as learning/accounts
# Will be fully implemented in Step 4 of migration

@router.get("/sources")
async def list_sources(skip=0, limit=20, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(get_current_user)):
    result = await db.execute(select(PuzzleSource).order_by(desc(PuzzleSource.created_at)).offset(skip).limit(limit))
    return [{"id": s.id, "name": s.name, "source_type": s.source_type, "status": s.status} for s in result.scalars().all()]


@router.get("/")
async def list_puzzles(skip=0, limit=20, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(get_current_user)):
    result = await db.execute(select(Puzzle).order_by(desc(Puzzle.created_at)).offset(skip).limit(limit))
    return [{"id": p.id, "title": p.title, "subject": p.subject, "difficulty": p.difficulty, "type": p.type} for p in result.scalars().all()]