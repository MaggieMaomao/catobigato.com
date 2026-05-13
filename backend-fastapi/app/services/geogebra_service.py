"""
GeoGebra Service — GGBScript generation and validation.

Phase 1 (stub): Rule-based expression → GGBScript
Phase 2: VisionSolverAgent — image → GGBScript via multi-stage LLM pipeline

GeoGebra JavaScript API reference:
https://wiki.geogebra.org/reference/Scripting
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Geometric keywords that trigger GeoGebra mode
GEOMETRIC_KEYWORDS = [
    "triangle", "circle", "angle", "perpendicular", "parallel",
    "bisector", "polygon", "ellipse", "hyperbola", "parabola",
    "midpoint", "intersect", "tangent", "secant", "chord",
    "arc", "sector", "segment", "vertex", "vertices",
    "quadrilateral", "rectangle", "square", "parallelogram",
    "trapezoid", "kite", "rhombus", "diameter", "radius",
    "circumference", "circumcircle", "incircle", "inscribed",
    "circumference", "area", "perimeter",
]

# Keywords that trigger animation mode
ANIMATION_KEYWORDS = [
    "animate", "show how", "demonstrate", "illustrate",
    "explain step", "draw slowly", "construction",
    "derive", "prove", "transform", "rotate", "reflect",
    "expand", "contract", "move", "trace",
]


def is_geometric_expression(expression: str) -> bool:
    """Detect if expression likely needs GeoGebra visualization."""
    expr_lower = expression.lower()
    if any(kw in expr_lower for kw in GEOMETRIC_KEYWORDS):
        return True
    # Parametric: (f(t), g(t))
    if re.search(r"\([^)]+\)\s*,\s*\(", expression):
        return True
    return False


def is_animation_worthy(expression: str) -> bool:
    """Detect if request describes a process to animate."""
    expr_lower = expression.lower()
    return any(kw in expr_lower for kw in ANIMATION_KEYWORDS)


def validate_ggb_command(command: str) -> tuple[bool, list[str]]:
    """Validate a single GGBScript command. Returns (is_valid, warnings)."""
    errors = []
    if not command.strip():
        return False, ["Empty command"]

    forbidden = ["Delete", "DeleteAll", "Remove", "Exec", "Open", "Run", "Save"]
    for cmd in forbidden:
        if re.match(rf"^\s*{cmd}\s*\(", command, re.IGNORECASE):
            return False, [f"Forbidden command: {cmd}"]

    if not re.match(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*$", command):
        return True, [f"Unrecognized command syntax: {command[:50]}"]

    return True, []


class GeoGebraService:
    """
    GeoGebra sketch generation service.

    Phase 1: Rule-based GGBScript generation for expressions.
    Phase 2: Full VisionSolverAgent pipeline for images.
    """

    def __init__(self):
        self.logger = logging.getLogger("services.geogebra")

    def suggest_mode(self, expression: str) -> str:
        """Determine whether to use 'latex', 'geogebra', or 'animate'."""
        if is_animation_worthy(expression):
            return "animate"
        if is_geometric_expression(expression):
            return "geogebra"
        return "latex"

    def generate_from_expression(self, expression: str) -> dict[str, Any]:
        """
        Convert a math expression to GGBScript commands.
        Handles: parametric curves, circles, functions, plain expressions.
        """
        self.logger.info(f"Generating from expression: {expression[:80]}")
        commands = []
        expr_stripped = expression.strip()

        # Parametric: (x(t), y(t))
        param_match = re.match(r"^\s*\(?([^,]+?)\s*,\s*([^)\s]+)\)?\s*$", expr_stripped)
        if param_match and ("(" in expr_stripped or "t" in expr_stripped):
            x_expr = param_match.group(1).strip()
            y_expr = param_match.group(2).strip()
            commands.append(f"Curve({x_expr}, {y_expr}, t, 0, 2*pi)")
            commands.append("SetColor(last, blue)")
            commands.append("SetLineThickness(last, 3)")
            return {"commands": commands, "is_geometric": True}

        # Circle: x^2 + y^2 = r^2
        circle_match = re.match(
            r"^x\s*\^\s*2\s*\+\s*y\s*\^\s*2\s*=\s*(\d+(?:\.\d+)?)\s*$",
            expr_stripped.replace(" ", "")
        )
        if circle_match:
            r = float(circle_match.group(1)) ** 0.5
            commands.append(f"c = Circle((0, 0), {r:.4f})")
            commands.append("SetColor(c, blue)")
            commands.append("SetLineThickness(c, 3)")
            return {"commands": commands, "is_geometric": True}

        # General function y = f(x)
        if "=" in expr_stripped:
            lhs = expr_stripped.split("=", 1)[0].strip()
            if lhs in ("y", "f(x)", "f"):
                rhs = expr_stripped.split("=", 1)[1].strip()
                commands.append(f"f(x) = {rhs}")
                commands.append("SetColor(f, blue)")
                return {"commands": commands, "is_geometric": True}

        # Plain expression → plot
        commands.append(f"Expression(a, b) = {expr_stripped}")
        return {"commands": commands, "is_geometric": False}

    async def generate_from_image(
        self,
        image_base64: str,
        question: str = "",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Analyze an image and generate GGBScript commands via VisionSolverAgent.
        Phase 2 implementation. Phase 1 stub returns error.
        """
        self.logger.warning(
            "generate_from_image called — Phase 1 stub. Use expression-based "
            "generation or wait for Phase 2 VisionSolverAgent."
        )
        return {
            "commands": [],
            "is_geometric": True,
            "error": "Image analysis (VisionSolverAgent) comes in Phase 2. "
                     "Use expression-based generation.",
        }