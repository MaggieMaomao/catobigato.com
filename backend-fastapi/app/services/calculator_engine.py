"""SymPy-powered calculator engine for FastAPI."""

from sympy import (
    sympify, simplify, factor, expand, solve, diff,
    Integral, plotting, Symbol, Eq, symbols, latex
)
from sympy.plotting import plot
from io import BytesIO, StringIO
import base64
import math


class CalculatorEngine:
    """Port of the Django CalculatorEngine to FastAPI/SQLAlchemy context."""

    def evaluate(self, expression: str) -> dict:
        """Evaluate a mathematical expression."""
        try:
            expr = sympify(expression)
            result = float(expr.evalf())
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

    def simplify(self, expression: str) -> dict:
        """Simplify an expression."""
        try:
            expr = sympify(expression)
            simplified = simplify(expr)
            return {
                "success": True,
                "simplified": str(simplified),
                "simplified_latex": latex(simplified),
                "expression": expression,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def factor(self, expression: str) -> dict:
        """Factor a polynomial."""
        try:
            expr = sympify(expression)
            factored = factor(expr)
            return {
                "success": True,
                "factored": str(factored),
                "factored_latex": latex(factored),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def expand(self, expression: str) -> dict:
        """Expand an expression."""
        try:
            expr = sympify(expression)
            expanded = expand(expr)
            return {
                "success": True,
                "expanded": str(expanded),
                "expanded_latex": latex(expanded),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def solve_equation(self, equation: str, variable: str = "x") -> dict:
        """Solve an equation."""
        try:
            eq = sympify(equation, evaluate=False)
            x = Symbol(variable)
            solutions = solve(eq, x)
            return {
                "success": True,
                "solutions": [str(s) for s in solutions],
                "solutions_latex": [latex(s) for s in solutions],
                "variable": variable,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def derivative(self, expression: str, variable: str = "x", order: int = 1) -> dict:
        """Compute derivative."""
        try:
            expr = sympify(expression)
            x = Symbol(variable)
            result = diff(expr, x, order)
            return {
                "success": True,
                "derivative": str(result),
                "derivative_latex": latex(result),
                "variable": variable,
                "order": order,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def integral(self, expression: str, variable: str = "x", lower=None, upper=None) -> dict:
        """Compute indefinite or definite integral."""
        try:
            expr = sympify(expression)
            x = Symbol(variable)
            if lower is not None and upper is not None:
                result = Integral(expr, (x, lower, upper)).doit()
            else:
                result = Integral(expr, x).doit()
            return {
                "success": True,
                "integral": str(result),
                "integral_latex": latex(result),
                "lower": lower,
                "upper": upper,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def plot_function(self, expression: str, variable: str = "x", x_range: tuple = (-10, 10), num_points: int = 500) -> dict:
        """Plot a function and return SVG as base64."""
        try:
            expr = sympify(expression)
            x = Symbol(variable)
            p = plot(expr, (x, x_range[0], x_range[1]), show=False, num_of_points=num_points)
            buf = BytesIO()
            p.save(buf)
            buf.seek(0)
            svg_bytes = buf.read()
            buf.close()
            # Clean SVG namespace for embedding
            svg_str = svg_bytes.decode("utf-8")
            # Remove XML declaration and extra whitespace
            svg_str = svg_str.replace('<?xml version="1.0" encoding="utf-8"?>', '').strip()
            return {
                "success": True,
                "svg": svg_str,
                "latex": latex(expr),
                "expression": expression,
                "variable": variable,
                "x_range": list(x_range),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate_function(self, func_def: dict, params: dict) -> dict:
        """Evaluate a user-defined function."""
        try:
            body = func_def.get("body", "")
            param_names = [p["name"] for p in func_def.get("params", [])]
            # Build expression with substituted values
            for name in param_names:
                val = params.get(name, 0)
                body = body.replace(name, str(val))
            result = sympify(body).evalf()
            return {"success": True, "result": float(result)}
        except Exception as e:
            return {"success": False, "error": str(e)}


engine = CalculatorEngine()