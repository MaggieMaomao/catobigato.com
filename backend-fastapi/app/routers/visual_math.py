"""VisualMath router — GeoGebra sketches and animation projects."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, CurrentUser
from app.models.visual_math import GeoGebraSketch, AnimationProject
from app.models.accounts import UserProfile
from app.schemas.visual_math import (
    GeoGebraSketchCreate,
    GeoGebraSketchUpdate,
    GeoGebraSketchResponse,
    AnimationProjectCreate,
    AnimationProjectUpdate,
    AnimationProjectResponse,
    AnimationStatusResponse,
    VisualMathSolveRequest,
    VisualMathSolveResponse,
    StageUpdate,
)
from app.services.visual_math_service import VisualMathService
import uuid

router = APIRouter(prefix="/visual-math", tags=["visual-math"])


def _sketch_to_response(s: GeoGebraSketch) -> GeoGebraSketchResponse:
    return GeoGebraSketchResponse(
        id=s.id, creator_id=s.creator_id, title=s.title, description=s.description,
        source=s.source, expression=s.expression, ggb_commands=s.ggb_commands,
        image_data=s.image_data, bbox_elements=s.bbox_elements,
        constraints=s.constraints, geometric_relations=s.geometric_relations,
        is_shared=s.is_shared,
        created_at=s.created_at.isoformat(), updated_at=s.updated_at.isoformat(),
    )


def _animation_to_response(a: AnimationProject) -> AnimationProjectResponse:
    return AnimationProjectResponse(
        id=a.id, creator_id=a.creator_id, title=a.title, description=a.description,
        user_input=a.user_input, concept_analysis=a.concept_analysis,
        scene_design=a.scene_design, generated_code=a.generated_code,
        rendered_output_url=a.rendered_output_url, output_mode=a.output_mode,
        quality=a.quality, status=a.status, error_message=a.error_message,
        celery_task_id=a.celery_task_id,
        created_at=a.created_at.isoformat(), updated_at=a.updated_at.isoformat(),
    )


def _stage_status(status: str) -> str:
    mapping = {"pending": "started", "analysis": "done", "design": "started",
               "coding": "done", "rendering": "started", "done": "done", "failed": "error"}
    return mapping.get(status, "done")


async def _get_or_create_profile(db: AsyncSession, user: CurrentUser) -> UserProfile:
    sub = uuid.UUID(user.sub)
    result = await db.execute(select(UserProfile).where(UserProfile.keycloak_sub == sub))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(keycloak_sub=sub, display_name=user.display_name)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile


@router.post("/solve", response_model=VisualMathSolveResponse)
async def solve(
    payload: VisualMathSolveRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Main VisualMath solve endpoint.
    Routes to latex / geogebra / animate based on content analysis.
    Phase 1: rule-based stub. Phase 2: full VisionSolverAgent pipeline.
    """
    service = VisualMathService()
    profile = await _get_or_create_profile(db, user)
    result = await service.solve(payload, profile)

    stages = []
    for name, data in result.get("stages", {}).items():
        stages.append(StageUpdate(
            stage=name,
            status=_stage_status(data.get("status", "done")),
            message=data.get("message", ""),
            data=data.get("data", {}),
        ))

    return VisualMathSolveResponse(
        mode=result.get("mode", "latex"),
        result=result.get("result", {}),
        sketch_id=result.get("sketch_id"),
        animation_id=result.get("animation_id"),
        stages=stages,
        warnings=result.get("warnings", []),
    )


# ── GeoGebra Sketch CRUD ────────────────────────────────────────

@router.get("/sketches", response_model=list[GeoGebraSketchResponse])
async def list_sketches(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(GeoGebraSketch)
        .where(GeoGebraSketch.creator_id == profile.id)
        .order_by(GeoGebraSketch.updated_at.desc())
        .offset(skip).limit(limit)
    )
    return [_sketch_to_response(s) for s in result.scalars().all()]


@router.post("/sketches", response_model=GeoGebraSketchResponse)
async def create_sketch(
    payload: GeoGebraSketchCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    sketch = GeoGebraSketch(creator_id=profile.id, **payload.model_dump())
    db.add(sketch)
    await db.flush()
    await db.refresh(sketch)
    return _sketch_to_response(sketch)


@router.get("/sketches/{sketch_id}", response_model=GeoGebraSketchResponse)
async def get_sketch(
    sketch_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(select(GeoGebraSketch).where(GeoGebraSketch.id == sketch_id))
    sketch = result.scalar_one_or_none()
    if not sketch:
        raise HTTPException(status_code=404, detail="Sketch not found")
    return _sketch_to_response(sketch)


@router.patch("/sketches/{sketch_id}", response_model=GeoGebraSketchResponse)
async def update_sketch(
    sketch_id: uuid.UUID,
    payload: GeoGebraSketchUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(GeoGebraSketch).where(GeoGebraSketch.id == sketch_id, GeoGebraSketch.creator_id == profile.id)
    )
    sketch = result.scalar_one_or_none()
    if not sketch:
        raise HTTPException(status_code=404, detail="Sketch not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(sketch, field, value)
    await db.flush()
    await db.refresh(sketch)
    return _sketch_to_response(sketch)


@router.delete("/sketches/{sketch_id}")
async def delete_sketch(
    sketch_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(GeoGebraSketch).where(GeoGebraSketch.id == sketch_id, GeoGebraSketch.creator_id == profile.id)
    )
    sketch = result.scalar_one_or_none()
    if not sketch:
        raise HTTPException(status_code=404, detail="Sketch not found")
    await db.delete(sketch)
    return {"ok": True}


# ── AnimationProject CRUD ───────────────────────────────────────

@router.get("/animations", response_model=list[AnimationProjectResponse])
async def list_animations(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(AnimationProject)
        .where(AnimationProject.creator_id == profile.id)
        .order_by(AnimationProject.updated_at.desc())
        .offset(skip).limit(limit)
    )
    return [_animation_to_response(a) for a in result.scalars().all()]


@router.post("/animations", response_model=AnimationProjectResponse)
async def create_animation(
    payload: AnimationProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    animation = AnimationProject(creator_id=profile.id, **payload.model_dump())
    db.add(animation)
    await db.flush()
    await db.refresh(animation)
    return _animation_to_response(animation)


@router.get("/animations/{animation_id}", response_model=AnimationProjectResponse)
async def get_animation(
    animation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(select(AnimationProject).where(AnimationProject.id == animation_id))
    animation = result.scalar_one_or_none()
    if not animation:
        raise HTTPException(status_code=404, detail="Animation not found")
    return _animation_to_response(animation)


@router.patch("/animations/{animation_id}", response_model=AnimationProjectResponse)
async def update_animation(
    animation_id: uuid.UUID,
    payload: AnimationProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(AnimationProject).where(AnimationProject.id == animation_id, AnimationProject.creator_id == profile.id)
    )
    animation = result.scalar_one_or_none()
    if not animation:
        raise HTTPException(status_code=404, detail="Animation not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(animation, field, value)
    await db.flush()
    await db.refresh(animation)
    return _animation_to_response(animation)


@router.get("/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(
    animation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(select(AnimationProject).where(AnimationProject.id == animation_id))
    animation = result.scalar_one_or_none()
    if not animation:
        raise HTTPException(status_code=404, detail="Animation not found")

    progress_map = {
        "pending": 0, "analysis": 25, "design": 50,
        "coding": 75, "rendering": 90, "done": 100, "failed": 0,
    }
    stage_map = {
        "pending": "Queued", "analysis": "Analyzing concept", "design": "Designing scene",
        "coding": "Generating code", "rendering": "Rendering", "done": "Done", "failed": "Failed",
    }

    return AnimationStatusResponse(
        id=animation.id,
        status=animation.status,
        stage=stage_map.get(animation.status, "—"),
        progress_pct=progress_map.get(animation.status, 0),
        output_url=animation.rendered_output_url,
        error=animation.error_message,
        celery_task_id=animation.celery_task_id,
    )


@router.delete("/animations/{animation_id}")
async def delete_animation(
    animation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = await _get_or_create_profile(db, user)
    result = await db.execute(
        select(AnimationProject).where(AnimationProject.id == animation_id, AnimationProject.creator_id == profile.id)
    )
    animation = result.scalar_one_or_none()
    if not animation:
        raise HTTPException(status_code=404, detail="Animation not found")
    await db.delete(animation)
    return {"ok": True}