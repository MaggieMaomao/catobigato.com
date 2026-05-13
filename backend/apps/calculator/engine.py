"""
Calculator Engine — SymPy-based expression parser and evaluator.
Handles: arithmetic, trigonometry, calculus (derivatives/integrals), algebra, graphing.
Used both for direct evaluation and as a fallback when client-side mathjs can't handle it.
"""

import re
import json
import math
import traceback
from typing import Any, Optional

import sympy
from sympy import (
    Symbol, symbols, sympify, simplify, solve, diff, integrate,
    sin, cos, tan, log, exp, sqrt, pi, E, Rational,
    latex, plot, plot_implicit, Eq,
    Function, symbols, sympify, parse_expr,
    solveset,
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    auto_symbol,
)
from sympy.plotting import plot as symplot
from sympy.core.sympify import SympifyError
from sympy.solvers.solveset import solveset


class CalculatorEngine:
    """
    Server-side calculator engine using SymPy.
    Provides:
    - Expression evaluation
    - Symbolic math (derivatives, integrals, solving equations)
    - Algebra (factorization, expansion, simplification)
    - Equation solving
    - Graph generation
    """

    def __init__(self):
        self.transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )
        self._reserved_names = {
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
            'log', 'ln', 'log10', 'exp', 'sqrt', 'cbrt',
            'abs', 'sign', 'floor', 'ceil',
            'pi', 'e', 'E',
            'diff', 'integrate', 'solve', 'simplify',
            'expand', 'factor', 'expand_trig',
        }

    def evaluate(self, expression: str, precision: int = 10) -> dict:
        """
        Evaluate a mathematical expression.
        Returns: {result, latex, success, error}
        """
        try:
            # Parse expression
            expr = parse_expr(expression, transformations=self.transformations)

            # Evaluate numerically with precision
            result = float(expr.evalf(precision))

            return {
                "success": True,
                "result": result,
                "latex": latex(expr),
                "expression": expression,
                "type": "numeric"
            }
        except SympifyError as e:
            return {
                "success": False,
                "error": f"Cannot parse expression: {e}",
                "expression": expression,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression,
            }

    def evaluate_with_vars(self, expression: str, variables: dict[str, float]) -> dict:
        """
        Evaluate expression with variable substitution.
        variables: {"x": 2, "y": 3}
        """
        try:
            # Substitute variables
            for name, value in variables.items():
                expr = parse_expr(expression, transformations=self.transformations)
                sym = Symbol(name)
                expr = expr.subs(sym, value)

            result = float(expr.evalf())

            return {
                "success": True,
                "result": result,
                "variables": variables,
                "expression": expression,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def simplify(self, expression: str) -> dict:
        """Simplify a symbolic expression."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            simplified = simplify(expr)
            return {
                "success": True,
                "original": expression,
                "simplified": latex(simplified),
                "simplified_raw": str(simplified),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def solve_equation(self, equation: str, variable: str = "x") -> dict:
        """
        Solve an equation or system.
        Examples:
            "x^2 - 4 = 0" → solutions
            "2*x + 3 = 7" → x = ?
        """
        try:
            var = Symbol(variable)
            # Parse equation (may have = or just an expression to set = 0)
            if "=" in equation:
                lhs, rhs = equation.split("=")
                expr = parse_expr(f"({lhs}) - ({rhs})", transformations=self.transformations)
            else:
                expr = parse_expr(equation, transformations=self.transformations)

            solutions = solve(expr, var)

            return {
                "success": True,
                "equation": equation,
                "variable": variable,
                "solutions": [str(s) for s in solutions],
                "solutions_latex": [latex(s) for s in solutions],
                "count": len(solutions),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def solve_system(self, equations: list[str], variables: list[str]) -> dict:
        """Solve a system of equations."""
        try:
            syms = [Symbol(v) for v in variables]
            parsed_eqs = [parse_expr(eq, transformations=self.transformations) for eq in equations]

            solutions = solve(parsed_eqs, syms)

            result = {}
            for sym, val in solutions.items():
                result[str(sym)] = str(val)

            return {
                "success": True,
                "equations": equations,
                "variables": variables,
                "solutions": result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def derivative(self, expression: str, variable: str = "x", order: int = 1) -> dict:
        """Compute derivative of expression."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            var = Symbol(variable)
            deriv = diff(expr, var, order)

            return {
                "success": True,
                "original": expression,
                "variable": variable,
                "order": order,
                "derivative": str(deriv),
                "derivative_latex": latex(deriv),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def integral(self, expression: str, variable: str = "x") -> dict:
        """Compute indefinite integral."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            var = Symbol(variable)
            integral = integrate(expr, var)

            return {
                "success": True,
                "original": expression,
                "variable": variable,
                "integral": str(integral),
                "integral_latex": latex(integral),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def definite_integral(self, expression: str, variable: str,
                          lower: float, upper: float) -> dict:
        """Compute definite integral."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            var = Symbol(variable)
            result = integrate(expr, (var, lower, upper))

            return {
                "success": True,
                "original": expression,
                "variable": variable,
                "lower": lower,
                "upper": upper,
                "result": float(result.evalf()),
                "result_latex": latex(result),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def factor(self, expression: str) -> dict:
        """Factorize a polynomial expression."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            factored = sympy.factor(expr)

            return {
                "success": True,
                "original": expression,
                "factored": str(factored),
                "factored_latex": latex(factored),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def expand(self, expression: str) -> dict:
        """Expand a factored expression."""
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            expanded = sympy.expand(expr)

            return {
                "success": True,
                "original": expression,
                "expanded": str(expanded),
                "expanded_latex": latex(expanded),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def plot_function(self, expression: str, variable: str = "x",
                      x_range: tuple = (-10, 10), num_points: int = 500) -> dict:
        """
        Generate plot data for a function.
        Returns points as JSON for SVG rendering on frontend.
        """
        try:
            expr = parse_expr(expression, transformations=self.transformations)
            var = Symbol(variable)

            # Generate points
            x_vals = []
            y_vals = []
            step = (x_range[1] - x_range[0]) / num_points

            x = x_range[0]
            while x <= x_range[1]:
                try:
                    y = float(expr.subs(var, x).evalf())
                    if math.isfinite(y):
                        x_vals.append(round(x, 6))
                        y_vals.append(round(y, 6))
                except (TypeError, ValueError):
                    pass
                x += step

            # Compute axis info
            y_min, y_max = min(y_vals), max(y_vals)
            y_range = max(abs(y_min), abs(y_max)) * 1.1

            return {
                "success": True,
                "expression": expression,
                "variable": variable,
                "x_range": list(x_range),
                "points": {"x": x_vals, "y": y_vals},
                "axis": {
                    "x_min": x_range[0],
                    "x_max": x_range[1],
                    "y_min": -y_range,
                    "y_max": y_range,
                    "y_zero": 0,
                },
                "latex": latex(expr),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def plot_implicit(self, equation: str, x_range: tuple = (-10, 10),
                      y_range: tuple = (-10, 10)) -> dict:
        """
        Generate plot for implicit equations (e.g., circles, curves).
        Returns grid data for the frontend to render.
        """
        try:
            if "=" in equation:
                lhs, rhs = equation.split("=")
                expr = parse_expr(f"({lhs}) - ({rhs})", transformations=self.transformations)
            else:
                expr = parse_expr(equation, transformations=self.transformations)

            # Generate grid of points
            x_vals = list(range(int(x_range[0]), int(x_range[1]) + 1, 1))
            y_vals = list(range(int(y_range[0]), int(y_range[1]) + 1, 1))

            # Create grid with distance from curve
            grid = []
            for y in y_vals:
                row = []
                for x in x_vals:
                    val = float(expr.subs(Symbol('x'), x).subs(Symbol('y'), y).evalf())
                    row.append(val)
                grid.append(row)

            return {
                "success": True,
                "equation": equation,
                "grid": grid,
                "x_range": list(x_range),
                "y_range": list(y_range),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate_custom_function(self, func_definition: dict,
                                  param_values: dict[str, float]) -> dict:
        """
        Evaluate a user-defined custom function.
        func_definition: {"params": [{"name": "x", "type": "number"}], "body": "x^2 + 1"}
        param_values: {"x": 5}
        """
        try:
            body = func_definition["body"]
            expr = parse_expr(body, transformations=self.transformations)

            # Substitute parameters
            for name, value in param_values.items():
                sym = Symbol(name)
                expr = expr.subs(sym, value)

            result = float(expr.evalf())

            return {
                "success": True,
                "function_body": body,
                "params": param_values,
                "result": result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def matrix_operations(self, matrix_a: list[list], matrix_b: list[list] = None,
                          operation: str = "determinant") -> dict:
        """
        Matrix operations: determinant, inverse, add, multiply.
        """
        try:
            import numpy as np

            A = np.array(matrix_a)
            if matrix_b is not None:
                B = np.array(matrix_b)

            if operation == "determinant":
                result = float(np.linalg.det(A))
            elif operation == "inverse":
                result = np.linalg.inv(A).tolist()
            elif operation == "add":
                result = (A + B).tolist()
            elif operation == "multiply":
                result = np.matmul(A, B).tolist()
            elif operation == "transpose":
                result = A.T.tolist()
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

            return {"success": True, "operation": operation, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
engine = CalculatorEngine()