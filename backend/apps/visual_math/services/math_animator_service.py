"""
Math Animator Service
======================

Manim-based math animation generation pipeline.
5-stage pipeline: ConceptAnalysis → ConceptDesign → CodeGen → Review → Render.

Stub for Phase 1. Full pipeline implementation in Phase 3.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Animation-worthy concepts
ANIMATION_KEYWORDS = [
    "animate", "show", "draw", "step", "construction",
    "process", "transform", "rotate", "reflect", "dilate",
    "sequence", "evolution", "motion", "movement",
    "limit", "derivative", "integral", "series",
    "converge", "diverge", "tangent", "secant",
    "area under curve", "slope", "graph", "plot",
]


def is_animation_worthy(request: str) -> bool:
    """Detect if a request is asking for an animation rather than static output."""
    request_lower = request.lower()
    for kw in ANIMATION_KEYWORDS:
        if kw in request_lower:
            return True
    # Multi-step processes suggest animation
    if request_lower.startswith(("show how", "explain how", "demonstrate", "illustrate")):
        return True
    return False


class MathAnimatorService:
    """
    Math animation generation service using Manim.

    Phase 1 (this stub):
        - Detect if a request warrants an animation
        - Return pipeline stage metadata (not real rendering)

    Phase 3 (full pipeline):
        - 5-stage LLM-powered pipeline
        - Celery task for Manim rendering
        - Progress streaming
    """

    def __init__(self):
        self.logger = logging.getLogger("visual_math.animator")

    def suggest_visual_mode(self, request: str) -> str:
        """Determine if request is best served by 'animate' mode."""
        if is_animation_worthy(request):
            return "animate"
        return "geogebra"  # fallback to GeoGebra for static geometry

    async def generate_animation(
        self,
        request: str,
        output_mode: str = "video",
        quality: str = "medium",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Generate a math animation from a natural-language request.

        Phase 1 stub: returns pipeline metadata, no real rendering.
        Phase 3 will dispatch a real Celery task.

        Returns:
            {
                "success": bool,
                "project_id": str (UUID),
                "status": str,
                "estimated_duration": str,
                "message": str,
            }
        """
        self.logger.info(f"MathAnimator received request: {request[:80]}")

        if not is_animation_worthy(request):
            return {
                "success": False,
                "project_id": None,
                "status": "rejected",
                "message": (
                    "Request does not appear to need animation. "
                    "Use a static expression or GeoGebra sketch instead."
                ),
                "suggested_mode": "geogebra",
            }

        # Phase 1 stub: create a project record but don't dispatch real rendering
        from apps.visual_math.models import AnimationProject

        project = AnimationProject.objects.create(
            title=request[:80],
            user_input=request,
            output_mode=output_mode,
            quality=quality,
            status="pending",
        )

        self.logger.info(f"Created AnimationProject stub: {project.id}")

        return {
            "success": True,
            "project_id": str(project.id),
            "status": "pending",
            "estimated_duration": self._estimate_duration(request),
            "message": (
                "Animation project created. Full rendering will be available "
                "in Phase 3 (MathAnimator pipeline + Celery worker)."
            ),
            "phase": 1,
        }

    def _estimate_duration(self, request: str) -> str:
        """Rough estimate of animation duration based on request complexity."""
        word_count = len(request.split())
        if word_count < 20:
            return "10-15 seconds"
        elif word_count < 50:
            return "20-30 seconds"
        else:
            return "30-60 seconds"

    async def get_project_status(self, project_id: str) -> dict[str, Any]:
        """Poll the current status of an animation project."""
        from apps.visual_math.models import AnimationProject
        from uuid import UUID

        try:
            project = AnimationProject.objects.get(id=UUID(project_id))
        except (AnimationProject.DoesNotExist, ValueError):
            return {"success": False, "error": "Project not found"}

        return {
            "success": True,
            "project_id": str(project.id),
            "status": project.status,
            "title": project.title,
            "rendered_output_url": project.rendered_output_url,
            "error_message": project.error_message,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }