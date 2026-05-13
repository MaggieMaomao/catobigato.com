"""
VisualMath Services
====================

Orchestrates GeoGebra and MathAnimator capabilities.
Each service can be used standalone or composed by VisualMathService.

Services:
    - geogebra_service:     Image → GGBScript via VisionSolverAgent (Phase 2)
    - math_animator_service: Text → Manim animation (Phase 3)
    - render_service:      Manim code → MP4/PNG (Phase 3)

This module also exposes the VisualMathService orchestrator that
composes calculator engine + visual services based on input type.
"""

from .geogebra_service import GeoGebraService
from .math_animator_service import MathAnimatorService
from .visual_math_service import VisualMathService

__all__ = [
    "GeoGebraService",
    "MathAnimatorService",
    "VisualMathService",
]