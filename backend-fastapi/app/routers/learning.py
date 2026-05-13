"""Learning router stub."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, CurrentUser
from app.models.learning import Note, Question, QuestionSet, ExamAttempt, StudyGroup
from app.schemas.learning import (
    NoteCreate, NoteUpdate, NoteResponse,
    QuestionCreate, QuestionResponse,
    QuestionSetCreate, QuestionSetResponse,
    ExamAttemptCreate, ExamAttemptResponse,
    StudyGroupCreate, StudyGroupResponse,
)
import uuid

router = APIRouter(prefix="/learning", tags=["learning"])

# ── Notes ────────────────────────────────────────────────────

@router.get("/notes", response_model=list[NoteResponse])
async def list_notes(skip=0, limit=20, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(Note).where(Note.creator_id == profile_id).order_by(desc(Note.updated_at)).offset(skip).limit(limit))
    return [_note(n) for n in result.scalars().all()]

@router.post("/notes", response_model=NoteResponse)
async def create_note(payload: NoteCreate, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    note = Note(creator_id=profile_id, **payload.model_dump())
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return _note(note)

@router.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: uuid.UUID, payload: NoteUpdate, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(Note).where(Note.id == note_id, Note.creator_id == profile_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await db.flush()
    await db.refresh(note)
    return _note(note)

@router.delete("/notes/{note_id}")
async def delete_note(note_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(Note).where(Note.id == note_id, Note.creator_id == profile_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    return {"ok": True}

# ── Questions ────────────────────────────────────────────────

@router.get("/questions", response_model=list[QuestionResponse])
async def list_questions(skip=0, limit=20, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(Question).where(Question.creator_id == profile_id).order_by(desc(Question.created_at)).offset(skip).limit(limit))
    return [_question(q) for q in result.scalars().all()]

@router.post("/questions", response_model=QuestionResponse)
async def create_question(payload: QuestionCreate, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    q = Question(creator_id=profile_id, **payload.model_dump())
    db.add(q)
    await db.flush()
    await db.refresh(q)
    return _question(q)

# ── Question Sets ─────────────────────────────────────────────

@router.get("/question-sets", response_model=list[QuestionSetResponse])
async def list_question_sets(skip=0, limit=20, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(QuestionSet).where(QuestionSet.creator_id == profile_id).order_by(desc(QuestionSet.created_at)).offset(skip).limit(limit))
    return [_qs(qs) for qs in result.scalars().all()]

@router.post("/question-sets", response_model=QuestionSetResponse)
async def create_question_set(payload: QuestionSetCreate, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    qs = QuestionSet(creator_id=profile_id, **payload.model_dump(exclude={"question_ids"}))
    db.add(qs)
    await db.flush()
    await db.refresh(qs)
    return _qs(qs)

# ── Study Groups ─────────────────────────────────────────────

@router.get("/groups", response_model=list[StudyGroupResponse])
async def list_groups(skip=0, limit=20, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    result = await db.execute(select(StudyGroup).order_by(desc(StudyGroup.created_at)).offset(skip).limit(limit))
    return [_group(g) for g in result.scalars().all()]

@router.post("/groups", response_model=StudyGroupResponse)
async def create_group(payload: StudyGroupCreate, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    profile_id = await _get_profile_id(db, user)
    g = StudyGroup(creator_id=profile_id, **payload.model_dump())
    db.add(g)
    await db.flush()
    await db.refresh(g)
    return _group(g)

# ── Helpers ──────────────────────────────────────────────────

async def _get_profile_id(db: AsyncSession, user: CurrentUser) -> uuid.UUID:
    from app.models.accounts import UserProfile
    sub = uuid.UUID(user.sub)
    result = await db.execute(select(UserProfile.keycloak_sub == sub))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(keycloak_sub=sub, display_name=user.display_name)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile.id

def _note(n) -> NoteResponse:
    return NoteResponse(id=n.id, creator_id=n.creator_id, title=n.title, content=n.content, subject=n.subject, tags=n.tags, is_shared=n.is_shared, created_at=n.created_at.isoformat(), updated_at=n.updated_at.isoformat())

def _question(q) -> QuestionResponse:
    return QuestionResponse(id=q.id, creator_id=q.creator_id, type=q.type, subject=q.subject, difficulty=q.difficulty, content=q.content, answer=q.answer, hints=q.hints, tags=q.tags, explanation=q.explanation, is_public=q.is_public, approved=q.approved, created_at=q.created_at.isoformat())

def _qs(qs) -> QuestionSetResponse:
    return QuestionSetResponse(id=qs.id, creator_id=qs.creator_id, title=qs.title, description=qs.description, subject=qs.subject, difficulty=qs.difficulty, time_limit=qs.time_limit, is_exam=qs.is_exam, is_public=qs.is_public, created_at=qs.created_at.isoformat())

def _group(g) -> StudyGroupResponse:
    return StudyGroupResponse(id=g.id, name=g.name, description=g.description, subject=g.subject, creator_id=g.creator_id, is_public=g.is_public, created_at=g.created_at.isoformat())