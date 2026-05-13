"""Puzzles models — mapped to existing Django tables."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Boolean, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PuzzleSource(Base):
    """Source of puzzles — manual, crawler, import."""

    __tablename__ = "puzzle_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    source_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    source_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    creator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Puzzle(Base):
    """Individual puzzle / problem."""

    __tablename__ = "puzzles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="problem_solving")
    subject: Mapped[str] = mapped_column(String(50), nullable=False, default="math")
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    solution: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    hints: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    curriculum_references: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    times_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    times_solved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    creator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
