"""VisualMath schemas — Pydantic request/response models."""

from pydantic import BaseModel
from typing import Optional
import uuid


# ── GeoGebraSketch ──────────────────────────────────────────────

class GeoGebraSketchBase(BaseModel):
    title: str = ""
    description: str = ""
    source: str = "manual"  # expression | image | manual
    expression: str = ""
    ggb_commands: str = ""


class GeoGebraSketchCreate(GeoGebraSketchBase):
    pass


class GeoGebraSketchUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ggb_commands: Optional[str] = None
    is_shared: Optional[bool] = None


class GeoGebraSketchResponse(GeoGebraSketchBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    image_data: str = ""
    bbox_elements: list = []
    constraints: list = []
    geometric_relations: list = []
    is_shared: bool = False
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ── AnimationProject ────────────────────────────────────────────

class AnimationProjectBase(BaseModel):
    title: str = ""
    description: str = ""
    user_input: str = ""
    output_mode: str = "video"
    quality: str = "medium"


class AnimationProjectCreate(AnimationProjectBase):
    pass


class AnimationProjectUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    generated_code: Optional[str] = None
    rendered_output_url: Optional[str] = None
    error_message: Optional[str] = None


class AnimationProjectResponse(AnimationProjectBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    concept_analysis: dict = {}
    scene_design: dict = {}
    generated_code: str = ""
    rendered_output_url: str = ""
    status: str = "pending"
    error_message: str = ""
    celery_task_id: str = ""
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AnimationStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    stage: str = ""
    progress_pct: int = 0
    output_url: str = ""
    error: str = ""
    celery_task_id: str = ""


# ── VisualMath solve endpoint ──────────────────────────────────

class VisualMathSolveRequest(BaseModel):
    expression: str
    mode: Optional[str] = None  # auto | latex | geogebra | animate
    image_base64: Optional[str] = None
    language: str = "en"
    quality: str = "medium"


class StageUpdate(BaseModel):
    stage: str
    status: str  # started | done | error
    message: str = ""
    data: dict = {}


class VisualMathSolveResponse(BaseModel):
    mode: str  # latex | geogebra | animate
    result: dict  # mode-specific result
    sketch_id: Optional[uuid.UUID] = None
    animation_id: Optional[uuid.UUID] = None
    stages: list[StageUpdate] = []
    warnings: list[str] = []