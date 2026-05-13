"""Calculator app views — API endpoints for calculation engine."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import CustomFunction, CalculationHistory
from .serializers import (
    CustomFunctionSerializer,
    CustomFunctionCreateSerializer,
    EvaluateRequestSerializer,
    PlotRequestSerializer,
    DerivativeRequestSerializer,
    IntegralRequestSerializer,
    SolveRequestSerializer,
    CalculationHistorySerializer,
)
from .engine import engine


# ─── Expression Evaluation ───────────────────────────────────────

class EvaluateView(APIView):
    """
    POST /api/v1/calculator/evaluate/
    Evaluate a mathematical expression using SymPy.
    """
    permission_classes = [AllowAny]  # Calculator is public for now

    def post(self, request):
        serializer = EvaluateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        expression = serializer.validated_data["expression"]
        variables = serializer.validated_data.get("variables", {})
        mode = serializer.validated_data["mode"]
        precision = serializer.validated_data.get("precision", 10)

        if variables:
            result = engine.evaluate_with_vars(expression, variables)
        else:
            result = engine.evaluate(expression, precision)

        # Record in history if user is authenticated
        if request.user.is_authenticated:
            # Get or create profile
            from apps.accounts.models import UserProfile
            profile = UserProfile.objects.filter(keycloak_sub=request.user.sub).first()
            if profile:
                CalculationHistory.objects.create(
                    user=profile,
                    mode=mode,
                    expression=expression,
                    result=str(result.get("result", result.get("error", ""))),
                    inputs=variables,
                )

        return Response(result)


class SimplifyView(APIView):
    """POST /api/v1/calculator/simplify/ — simplify an expression."""
    permission_classes = [AllowAny]

    def post(self, request):
        expression = request.data.get("expression", "")
        result = engine.simplify(expression)
        return Response(result)


class FactorView(APIView):
    """POST /api/v1/calculator/factor/ — factorize expression."""
    permission_classes = [AllowAny]

    def post(self, request):
        expression = request.data.get("expression", "")
        result = engine.factor(expression)
        return Response(result)


class ExpandView(APIView):
    """POST /api/v1/calculator/expand/ — expand expression."""
    permission_classes = [AllowAny]

    def post(self, request):
        expression = request.data.get("expression", "")
        result = engine.expand(expression)
        return Response(result)


# ─── Equation Solving ──────────────────────────────────────────────

class SolveEquationView(APIView):
    """POST /api/v1/calculator/solve/ — solve an equation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SolveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = engine.solve_equation(
            serializer.validated_data["equation"],
            serializer.validated_data.get("variable", "x")
        )
        return Response(result)


class SolveSystemView(APIView):
    """POST /api/v1/calculator/solve-system/ — solve a system of equations."""
    permission_classes = [AllowAny]

    def post(self, request):
        equations = request.data.get("equations", [])
        variables = request.data.get("variables", [])

        if not equations or not variables:
            return Response(
                {"error": "equations and variables are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = engine.solve_system(equations, variables)
        return Response(result)


# ─── Calculus ──────────────────────────────────────────────────────

class DerivativeView(APIView):
    """POST /api/v1/calculator/derivative/ — compute derivative."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DerivativeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = engine.derivative(
            serializer.validated_data["expression"],
            serializer.validated_data.get("variable", "x"),
            serializer.validated_data.get("order", 1)
        )
        return Response(result)


class IntegralView(APIView):
    """POST /api/v1/calculator/integrate/ — compute integral (indefinite or definite)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = IntegralRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lower = serializer.validated_data.get("lower")
        upper = serializer.validated_data.get("upper")

        if lower is not None and upper is not None:
            result = engine.definite_integral(
                serializer.validated_data["expression"],
                serializer.validated_data.get("variable", "x"),
                lower, upper
            )
        else:
            result = engine.integral(
                serializer.validated_data["expression"],
                serializer.validated_data.get("variable", "x")
            )
        return Response(result)


# ─── Graphing ──────────────────────────────────────────────────────

class PlotFunctionView(APIView):
    """POST /api/v1/calculator/plot/ — generate plot data for a function."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PlotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = engine.plot_function(
            serializer.validated_data["expression"],
            serializer.validated_data.get("variable", "x"),
            tuple(serializer.validated_data.get("x_range", [-10, 10])),
            serializer.validated_data.get("num_points", 500)
        )
        return Response(result)


class PlotImplicitView(APIView):
    """POST /api/v1/calculator/plot-implicit/ — plot implicit equation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PlotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = engine.plot_implicit(
            serializer.validated_data["expression"],
            tuple(serializer.validated_data.get("x_range", [-10, 10])),
            tuple(serializer.validated_data.get("y_range", [-10, 10]))
        )
        return Response(result)


# ─── Custom Functions ─────────────────────────────────────────────

class CustomFunctionListView(generics.ListCreateAPIView):
    """
    GET: List user's custom functions (public + own)
    POST: Create a new custom function
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CustomFunctionCreateSerializer
        return CustomFunctionSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return CustomFunction.objects.filter(
            models.Q(creator=profile) | models.Q(is_public=True)
        )

    def perform_create(self, serializer):
        profile = self.request.user.profile
        serializer.save(creator=profile)


class CustomFunctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE: Manage a specific custom function.
    Only the creator can modify or delete.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomFunctionSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return CustomFunction.objects.filter(
            models.Q(creator=profile) | models.Q(is_public=True)
        )

    def perform_update(self, serializer):
        # Only creator can update
        if serializer.instance.creator != self.request.user.profile:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the creator can update this function")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creator != self.request.user.profile:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the creator can delete this function")
        instance.delete()


class EvaluateCustomFunctionView(APIView):
    """
    POST /api/v1/calculator/functions/<id>/evaluate/
    Evaluate a custom function with provided parameters.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.db.models import Q

        profile = request.user.profile
        try:
            func = CustomFunction.objects.get(
                Q(id=pk) & (Q(creator=profile) | Q(is_public=True))
            )
        except CustomFunction.DoesNotExist:
            return Response(
                {"error": "Function not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        param_values = request.data.get("params", {})
        if not param_values:
            return Response(
                {"error": "params is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = engine.evaluate_custom_function(func.definition, param_values)
        return Response(result)


# ─── History ───────────────────────────────────────────────────────

class CalculationHistoryView(generics.ListAPIView):
    """GET: List current user's calculation history."""
    serializer_class = CalculationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = request.user.profile
        return CalculationHistory.objects.filter(user=profile)[:100]

    def delete(self, request):
        """DELETE: Clear all history for current user."""
        profile = request.user.profile
        deleted, _ = CalculationHistory.objects.filter(user=profile).delete()
        return Response({"deleted": deleted})


# Need to import models for Q
from django.db import models