"""
GeoGebra Service
=================

Provides GeoGebra sketch generation from:
1. Math expressions (direct GGBScript generation)
2. Images (via VisionSolverAgent — Phase 2)

Stub for Phase 1. Full 4-stage VisionSolver pipeline comes in Phase 2.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# Geometric keywords that suggest a GeoGebra approach
GEOMETRIC_KEYWORDS = [
    "triangle", "circle", "angle", "perpendicular", "parallel",
    "bisector", "polygon", "ellipse", "hyperbola", "parabola",
    "midpoint", "intersect", "tangent", "secant", "chord",
    "arc", "sector", "segment", "vertex", "vertices",
    "quadrilateral", "rectangle", "square", "parallelogram",
    "trapezoid", "kite", "rhombus", "diameter", "radius",
    "circumference", "area", "perimeter",
]

# Functions that produce geometric output
GEOMETRIC_FUNCTIONS = [
    "sin", "cos", "tan", "plot", "parametric",
]


def is_geometric_expression(expression: str) -> bool:
    """Detect if an expression likely needs GeoGebra visualization."""
    expr_lower = expression.lower()
    for kw in GEOMETRIC_KEYWORDS:
        if kw in expr_lower:
            return True
    # Check for parametric plots (e.g., (cos(t), sin(t)))
    if re.search(r"\([^)]+\)\s*,\s*\(", expression):
        return True
    return False


def expression_to_ggb_commands(expression: str) -> list[str]:
    """
    Convert a SymPy-compatible expression to GeoGebra commands.

    This is a rule-based stub for Phase 1. Phase 2 will replace this
    with the full VisionSolverAgent pipeline (LLM-powered).

    Handles common patterns:
    - y = f(x)          → function + graph
    - x^2 + y^2 = r^2   → circle
    - (x-h)^2 + (y-k)^2 → circle with center
    - parametric curves  → sequence of points or locus
    """
    commands = []
    expr_stripped = expression.strip()

    # Parametric curve: (f(t), g(t))
    parametric_match = re.match(
        r"^\s*\(?([^,]+?)\s*,\s*([^\)]+?)\)?\s*$", expr_stripped
    )
    if parametric_match:
        x_expr = parametric_match.group(1).strip()
        y_expr = parametric_match.group(2).strip()
        t = "t"
        commands.append(f"f(x,y)={x_expr}-{y_expr}")
        commands.append(f"Curve({x_expr}, {y_expr}, {t}, 0, 2*pi)")
        return commands

    # Implicit circle: x^2 + y^2 = r^2
    circle_match = re.match(
        r"^x\s*\^\s*2\s*\+\s*y\s*\^\s*2\s*=\s*(\d+(?:\.\d+)?)\s*$",
        expr_stripped.replace(" ", "")
    )
    if circle_match:
        r = float(circle_match.group(1)) ** 0.5
        commands.append(f"c = Circle((0, 0), {r:.4f})")
        commands.append(f"SetColor(c, blue)")
        commands.append(f"SetLineThickness(c, 3)")
        return commands

    # General function y = f(x)
    if "=" in expr_stripped and expr_stripped.split("=")[0].strip() in ["y", "f(x)", "f"]:
        rhs = expr_stripped.split("=", 1)[1].strip()
        safe_name = "f"
        commands.append(f"{safe_name}(x) = {rhs}")
        commands.append(f"SetColor({safe_name}, blue)")
        return commands

    # Plain expression → plot as function
    commands.append(f"Expression(a, b) = {expr_stripped}")
    return commands


def validate_ggb_command(command: str) -> tuple[bool, list[str]]:
    """
    Validate a single GGBScript command.
    Returns (is_valid, list_of_errors_or_warnings).
    """
    errors = []
    warnings = []

    # Must not be empty
    if not command.strip():
        return False, ["Empty command"]

    # Basic syntax: no dangerous commands
    forbidden = ["Delete", "DeleteAll", "Remove", "Exec", "Open", "Run"]
    for cmd in forbidden:
        if re.match(rf"^\s*{cmd}\s*\(", command, re.IGNORECASE):
            errors.append(f"Forbidden command: {cmd}")
            return False, errors

    # Must look like a GeoGebra command: Word(...)
    if not re.match(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*$", command):
        warnings.append(f"Unrecognized GeoGebra command syntax: {command[:50]}")

    return len(errors) == 0, warnings


class GeoGebraService:
    """
    GeoGebra sketch generation service.

    Phase 1 (this stub):
        - Detect if expression needs GeoGebra
        - Rule-based GGBScript generation for simple cases
        - Command validation

    Phase 2 (VisionSolverAgent):
        - Full 4-stage pipeline for image → GGBScript
        - LLM-powered command generation for complex cases
    """

    def __init__(self):
        self.logger = logging.getLogger("visual_math.geogebra")

    def suggest_visual_mode(self, expression: str) -> str:
        """Determine whether to use 'latex', 'geogebra', or 'animate'."""
        if is_geometric_expression(expression):
            return "geogebra"
        return "latex"

    def generate_from_expression(self, expression: str) -> dict[str, Any]:
        """
        Generate GeoGebra commands from a math expression.

        Returns:
            {
                "success": bool,
                "commands": list[str],  # GGBScript commands
                "is_geometric": bool,
                "fallback_latex": str,  # LaTeX if commands are empty
            }
        """
        self.logger.info(f"Generating GeoGebra from expression: {expression[:80]}")

        if not is_geometric_expression(expression):
            return {
                "success": False,
                "commands": [],
                "is_geometric": False,
                "fallback_latex": expression,
                "reason": "Expression does not appear to be geometric",
            }

        commands = expression_to_ggb_commands(expression)

        # Validate all commands
        all_valid = True
        all_warnings = []
        for cmd in commands:
            valid, warnings = validate_ggb_command(cmd)
            if not valid:
                all_valid = False
            all_warnings.extend(warnings)

        self.logger.info(f"Generated {len(commands)} commands, valid={all_valid}")

        return {
            "success": all_valid and len(commands) > 0,
            "commands": commands,
            "is_geometric": True,
            "warnings": all_warnings,
        }

    async def generate_from_image(
        self,
        image_base64: str,
        question: str = "",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Analyze an image and generate GeoGebra commands.

        Phase 2 will wire this to VisionSolverAgent.
        For Phase 1, returns a clear stub response.
        """
        self.logger.warning(
            "GeoGebraService.generate_from_image called but Phase 1 stub does not "
            "support image analysis. Use expression-based generation instead, "
            "or wait for Phase 2 VisionSolverAgent port."
        )
        return {
            "success": False,
            "commands": [],
            "error": "Image analysis (VisionSolverAgent) is not yet implemented. "
                     "This feature will be available in Phase 2.",
            "phase": 1,
        }