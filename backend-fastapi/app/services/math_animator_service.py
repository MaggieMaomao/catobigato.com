"""
Math Animator Service — Manim scene generation for math animations.

Phase 1 (stub): Keyword detection + placeholder response
Phase 3: Full MathAnimatorPipeline with Manim code generation

Manim rendering requires:
- Manim installed in a render worker (separate process/container)
- Scene code → subprocess → MP4/PNG output
- Celery task queues the rendering job
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Stage definitions (mirrors DeepTutor's pipeline stages)
STAGE_DEFINITIONS = {
    "concept_analysis": {
        "description": "Understanding what to animate and how",
        "default_duration": "short",
    },
    "scene_design": {
        "description": "Designing camera, objects, layout, animations",
        "default_duration": "medium",
    },
    "code_generation": {
        "description": "Writing Manim Python code for the scene",
        "default_duration": "medium",
    },
    "rendering": {
        "description": "Running Manim to produce video/image",
        "default_duration": "long",
    },
}

# Quality presets
QUALITY_PRESETS = {
    "low": {"resolution": "480p", "fps": 15, "loop": False},
    "medium": {"resolution": "720p", "fps": 30, "loop": False},
    "high": {"resolution": "1080p", "fps": 60, "loop": False},
}


def is_animation_request(text: str) -> bool:
    """Check if the request describes an animation-worthy concept."""
    keywords = [
        "animate", "show how", "demonstrate", "illustrate", "explain step",
        "draw", "construction", "derive", "prove", "transform", "rotate",
        "reflect", "expand", "contract", "move", "trace", "evolution",
        "process", "step by step",
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


class MathAnimatorService:
    """
    Math animation generation service.

    Phase 1: Keyword detection → AnimationProject created with 'pending' status.
    Phase 3: Full pipeline → Manim code → Celery render task → MP4 output.
    """

    def __init__(self):
        self.logger = logging.getLogger("services.math_animator")

    def is_animation_worthy(self, text: str) -> bool:
        return is_animation_request(text)

    def prepare_animation(
        self,
        user_input: str,
        quality: str = "medium",
        output_mode: str = "video",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Prepare animation metadata without generating code yet.
        Phase 1: returns placeholder metadata.
        Phase 3: calls MathAnimatorPipeline.
        """
        self.logger.info(f"Preparing animation for: {user_input[:80]}")

        preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])

        return {
            "title": user_input[:60] + ("..." if len(user_input) > 60 else ""),
            "description": user_input,
            "quality": quality,
            "output_mode": output_mode,
            "stages": STAGE_DEFINITIONS,
            "quality_preset": preset,
            "estimated_duration_seconds": 10 if quality == "low" else 30 if quality == "medium" else 60,
            "note": "Phase 1 stub — full pipeline in Phase 3",
        }

    async def generate_manim_code(
        self,
        concept_analysis: dict,
        scene_design: dict,
        quality: str = "medium",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Generate Manim Python code for a scene.
        Phase 3: Real LLM-powered code generation.
        Phase 1: Returns error stub.
        """
        self.logger.warning(
            "generate_manim_code called — Phase 1 stub. "
            "Use the /animations endpoint to create a project; "
            "full code generation comes in Phase 3."
        )
        return {
            "code": "",
            "error": "Manim code generation (Phase 3) not yet implemented. "
                     "Create an AnimationProject via POST /visual-math/animations.",
        }

    def get_stage_definition(self, stage: str) -> dict[str, Any]:
        return STAGE_DEFINITIONS.get(stage, {"description": "Unknown stage"})