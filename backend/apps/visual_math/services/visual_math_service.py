"""
VisualMath Service — Orchestrator
==================================

Composes CalculatorEngine + GeoGebraService + MathAnimatorService
into a unified visual math service.

Determines the best visual output mode based on the user's request
and routes to the appropriate sub-service.
"""

from __future__ import annotations

import logging
from typing import Any

from apps.calculator.engine import engine
from .geogebra_service import GeoGebraService, is_geometric_expression
from .math_animator_service import MathAnimatorService, is_animation_worthy

logger = logging.getLogger(__name__)


class VisualMathService:
    """
    Unified visual math orchestrator.

    Usage:
        service = VisualMathService()
        result = await service.solve(user_input, mode="auto", ...)
    """

    def __init__(self):
        self.geogebra = GeoGebraService()
        self.animator = MathAnimatorService()
        self.logger = logging.getLogger("visual_math")

    async def solve(
        self,
        user_input: str,
        mode: str = "auto",
        output_mode: str = "video",
        quality: str = "medium",
        language: str = "en",
        image_base64: str = "",
    ) -> dict[str, Any]:
        """
        Main entry point for visual math requests.

        Args:
            user_input: Math expression, question, or animation request
            mode: "auto" | "latex" | "geogebra" | "animate"
            output_mode: "video" | "image" (for animations)
            quality: "low" | "medium" | "high" (for animations)
            language: "en" | "zh"
            image_base64: Optional image for GeoGebra analysis

        Returns:
            Unified result dict with type-specific output:
            - type: "latex" | "geogebra" | "animate"
            - result: sub-service output
        """
        # Auto-detect mode
        if mode == "auto":
            mode = self._detect_mode(user_input, image_base64)
            self.logger.info(f"Auto-detected mode: {mode}")

        self.logger.info(f"VisualMathService.solve mode={mode} input={user_input[:60]}")

        if image_base64:
            # Image-based: always GeoGebra (Phase 2) or error stub
            return await self._handle_geogebra_image(user_input, image_base64, language)

        if mode == "geogebra":
            return await self._handle_geogebra_expression(user_input)

        if mode == "animate":
            return await self._handle_animate(user_input, output_mode, quality, language)

        # mode == "latex" or fallback
        return await self._handle_latex(user_input)

    def _detect_mode(self, user_input: str, image_base64: str) -> str:
        """Auto-detect the best visual mode from user input."""
        if image_base64:
            return "geogebra"
        if is_animation_worthy(user_input):
            return "animate"
        if is_geometric_expression(user_input):
            return "geogebra"
        return "latex"

    async def _handle_geogebra_expression(self, expression: str) -> dict[str, Any]:
        """Handle GeoGebra generation from expression."""
        result = self.geogebra.generate_from_expression(expression)
        if result["success"]:
            return {
                "type": "geogebra",
                "commands": result["commands"],
                "expression": expression,
                "warnings": result.get("warnings", []),
            }
        # Fallback to LaTeX if not geometric
        return await self._handle_latex_fallback(expression, result.get("reason", ""))

    async def _handle_geogebra_image(
        self, question: str, image_base64: str, language: str
    ) -> dict[str, Any]:
        """Handle GeoGebra generation from image (Phase 2 stub)."""
        result = await self.geogebra.generate_from_image(
            image_base64=image_base64,
            question=question,
            language=language,
        )
        if result["success"]:
            return {
                "type": "geogebra",
                "commands": result["commands"],
                "source": "image",
                "bbox_elements": result.get("bbox_elements", []),
            }
        return {
            "type": "error",
            "message": result.get("error", "Image analysis failed"),
            "phase": result.get("phase", 1),
        }

    async def _handle_animate(
        self, request: str, output_mode: str, quality: str, language: str
    ) -> dict[str, Any]:
        """Handle animation generation request."""
        result = await self.animator.generate_animation(
            request=request,
            output_mode=output_mode,
            quality=quality,
            language=language,
        )
        return {
            "type": "animate",
            "project_id": result.get("project_id"),
            "status": result.get("status"),
            "estimated_duration": result.get("estimated_duration"),
            "message": result.get("message"),
            "phase": result.get("phase", 1),
        }

    async def _handle_latex(self, expression: str) -> dict[str, Any]:
        """Handle LaTeX rendering from expression."""
        result = engine.evaluate(expression)
        return {
            "type": "latex",
            "result": result.get("result"),
            "latex": result.get("latex"),
            "expression": expression,
            "success": result.get("success", False),
        }

    async def _handle_latex_fallback(
        self, expression: str, reason: str
    ) -> dict[str, Any]:
        """Fallback to LaTeX when GeoGebra fails."""
        self.logger.info(f"GeoGebra fallback to LaTeX: {reason}")
        return await self._handle_latex(expression)

    # ─── Synchronous convenience methods ───────────────────────────────

    def suggest_mode(self, user_input: str, image_base64: str = "") -> str:
        """Non-async mode suggestion."""
        return self._detect_mode(user_input, image_base64)