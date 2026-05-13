"""VisualMath app — GeoGebraSketch and AnimationProject."""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class GeoGebraSketch(Base):
    __tablename__ = "geogebra_sketches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(20), default="manual")  # expression | image | manual
    expression: Mapped[str] = mapped_column(Text, default="")
    ggb_commands: Mapped[str] = mapped_column(Text, default="")
    image_data: Mapped[str] = mapped_column(Text, default="")  # base64
    bbox_elements: Mapped[list] = mapped_column(JSONB, default=list)
    constraints: Mapped[list] = mapped_column(JSONB, default=list)
    geometric_relations: Mapped[list] = mapped_column(JSONB, default=list)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator: Mapped["UserProfile"] = relationship("UserProfile", back_populates="geogebra_sketches")


class AnimationProject(Base):
    __tablename__ = "animation_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    user_input: Mapped[str] = mapped_column(Text, default="")
    concept_analysis: Mapped[dict] = mapped_column(JSONB, default=dict)
    scene_design: Mapped[dict] = mapped_column(JSONB, default=dict)
    generated_code: Mapped[str] = mapped_column(Text, default="")
    rendered_output_url: Mapped[str] = mapped_column(String(500), default="")
    output_mode: Mapped[str] = mapped_column(String(10), default="video")  # video | image
    quality: Mapped[str] = mapped_column(String(10), default="medium")  # low | medium | high
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | analysis | design | coding | rendering | done | failed
    error_message: Mapped[str] = mapped_column(Text, default="")
    celery_task_id: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator: Mapped["UserProfile"] = relationship("UserProfile", back_populates="animation_projects")