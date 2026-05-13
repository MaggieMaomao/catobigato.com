"""
VisualMath Orchestrator Service
===============================

Routes VisualMath requests to the appropriate service:
- LaTeX: render math expressions
- GeoGebra: generate GGBScript from expressions (Phase 1)
- Animation: create AnimationProject for math animations

Phase 1: rule-based routing + stub services
Phase 2: VisionSolverAgent for image → GGBScript
Phase 3: MathAnimatorPipeline for animation generation
"""

import logging
from typing import Any
from app.services.geogebra_service import GeoGebraService, is_geometric_expression, is_animation_worthy
from app.services.math_animator_service import MathAnimatorService
from app.schemas.visual_math import VisualMathSolveRequest

logger = logging.getLogger(__name__)


class VisualMathService:
    """
    Main orchestrator for VisualMath feature.

    Routes based on content analysis or explicit mode override.
    """

    def __init__(self):
        self.geogebra = GeoGebraService()
        self.animator = MathAnimatorService()
        self.logger = logging.getLogger("services.visual_math")

    def _detect_mode(self, expression: str) -> str:
        if is_animation_worthy(expression):
            return "animate"
        if is_geometric_expression(expression):
            return "geogebra"
        return "latex"

    async def solve(
        self,
        payload: VisualMathSolveRequest,
        profile,
    ) -> dict[str, Any]:
        """
        Main solve endpoint. Routes to appropriate service.
        Returns a dict with mode, result, stages, sketch_id/animation_id.
        """
        mode = payload.mode or self._detect_mode(payload.expression)
        self.logger.info(f"VisualMath solve — mode={mode}, expression={payload.expression[:60]}")

        if mode == "animate":
            return await self._solve_animate(payload, profile)
        elif mode == "geogebra":
            return await self._solve_geogebra(payload, profile)
        else:
            return self._solve_latex(payload)

    def _solve_latex(self, payload: VisualMathSolveRequest) -> dict[str, Any]:
        """Render expression as LaTeX (static math formatting)."""
        return {
            "mode": "latex",
            "result": {
                "latex": payload.expression,
                "html": f"<code>{payload.expression}</code>",
            },
            "stages": {
                "render": {"status": "done", "message": "LaTeX rendering (Phase 1)"}
            },
            "warnings": [],
        }

    async def _solve_geogebra(
        self,
        payload: VisualMathSolveRequest,
        profile,
    ) -> dict[str, Any]:
        """Generate GeoGebra sketch from expression. Phase 1 rule-based stub."""
        result = self.geogebra.generate_from_expression(payload.expression)

        if not result.get("is_geometric", False):
            return {
                "mode": "geogebra",
                "result": {"fallback_latex": payload.expression},
                "stages": {
                    "generation": {"status": "done", "message": "Not geometric — falling back to LaTeX"}
                },
                "warnings": result.get("warnings", []),
            }

        commands = result.get("commands", [])
        if not commands:
            return {
                "mode": "geogebra",
                "result": {"fallback_latex": payload.expression},
                "stages": {
                    "generation": {"status": "done", "message": "No commands generated"}
                },
                "warnings": ["No GeoGebra commands generated for this expression"],
            }

        return {
            "mode": "geogebra",
            "result": {
                "commands": commands,
                "ggb_script": "\n".join(commands),
                "is_geometric": True,
            },
            "stages": {
                "detection": {"status": "done", "message": "Geometric expression detected"},
                "generation": {
                    "status": "done",
                    "message": f"Generated {len(commands)} GGBScript commands",
                    "data": {"command_count": len(commands)},
                },
            },
            "warnings": result.get("warnings", []),
        }

    async def _solve_animate(
        self,
        payload: VisualMathSolveRequest,
        profile,
    ) -> dict[str, Any]:
        """Create an animation project. Phase 1 returns pending project stub."""
        preparation = self.animator.prepare_animation(
            user_input=payload.expression,
            quality=payload.quality,
            output_mode="video",
            language=payload.language,
        )

        return {
            "mode": "animate",
            "result": {
                "status": "pending",
                "message": "Animation project created. Full rendering comes in Phase 3.",
                "preparation": preparation,
            },
            "stages": {
                "concept_analysis": {
                    "status": "done",
                    "message": "Concept analysis (Phase 1 stub)",
                    "data": preparation,
                },
                "scene_design": {
                    "status": "done",
                    "message": "Scene design (Phase 1 stub)",
                },
                "code_generation": {
                    "status": "pending",
                    "message": "Manim code generation (Phase 3)",
                },
                "rendering": {
                    "status": "pending",
                    "message": "Manim rendering (Phase 3 + Celery worker)",
                },
            },
            "warnings": ["Animation rendering is Phase 3 — currently pending"],
        }