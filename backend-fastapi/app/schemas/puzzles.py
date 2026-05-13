"""Puzzles schemas."""

from pydantic import BaseModel
import uuid


class PuzzleSourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    source_url: str = ""
    status: str
    created_at: str

    class Config:
        from_attributes = True


class PuzzleResponse(BaseModel):
    id: uuid.UUID
    title: str
    type: str
    subject: str
    difficulty: str
    content: dict = {}
    solution: dict = {}
    hints: list[str] = []
    tags: list[str] = []
    status: str
    created_at: str

    class Config:
        from_attributes = True