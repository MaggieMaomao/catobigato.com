"""Learning schemas."""

from pydantic import BaseModel
from typing import Optional
import uuid


class NoteCreate(BaseModel):
    title: str = ""
    content: dict = {}
    subject: str = "general"
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    subject: Optional[str] = None
    tags: Optional[list[str]] = None
    is_shared: Optional[bool] = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    content: dict
    subject: str
    tags: list[str]
    is_shared: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    type: str
    subject: str = "general"
    difficulty: str = "medium"
    content: dict = {}
    answer: dict = {}
    hints: list[str] = []
    tags: list[str] = []
    explanation: dict = {}


class QuestionResponse(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    type: str
    subject: str
    difficulty: str
    content: dict
    answer: dict
    hints: list[str]
    tags: list[str]
    explanation: dict
    is_public: bool
    approved: bool
    created_at: str

    class Config:
        from_attributes = True


class QuestionSetCreate(BaseModel):
    title: str = ""
    description: str = ""
    subject: str = "general"
    difficulty: str = "medium"
    time_limit: int = 0
    is_exam: bool = False
    question_ids: list[uuid.UUID] = []


class QuestionSetResponse(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: str
    subject: str
    difficulty: str
    time_limit: int
    is_exam: bool
    is_public: bool
    created_at: str

    class Config:
        from_attributes = True


class ExamAttemptCreate(BaseModel):
    question_set_id: uuid.UUID
    answers: dict = {}


class ExamAttemptResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    question_set_id: uuid.UUID
    answers: dict
    score: Optional[float] = None
    max_score: Optional[float] = None
    status: str
    started_at: str
    submitted_at: Optional[str] = None

    class Config:
        from_attributes = True


class StudyGroupCreate(BaseModel):
    name: str
    description: str = ""
    subject: str = "general"
    is_public: bool = True


class StudyGroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    subject: str
    creator_id: uuid.UUID
    is_public: bool
    created_at: str

    class Config:
        from_attributes = True