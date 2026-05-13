"""VisualMath app views — API endpoints."""

import asyncio
import logging

from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile

from .models import GeoGebraSketch, AnimationProject
from .serializers import (
    AnimationProjectSerializer,
    AnimationStatusSerializer,
    GeoGebraSketchSerializer,
    VisualMathRequestSerializer,
)
from .services import VisualMathService

logger = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────

def get_user_profile(request) -> UserProfile | None:
    """Get UserProfile from request (Keycloak-authenticated)."""
    if not request.user.is_authenticated:
        return None
    return UserProfile.objects.filter(keycloak_sub=request.user.sub).first()


# ─── Main Solve Endpoint ──────────────────────────────────────────────

class VisualMathSolveView(APIView):
    """
    POST /api/v1/visual-math/solve/

    Unified visual math endpoint. Takes a math expression, question,
    or animation request and routes to the appropriate service
    (LaTeX, GeoGebra, or MathAnimator).

    Phase 1: GeoGebra = rule-based stub, Animator = project creation stub.
    Phase 2: GeoGebra = VisionSolverAgent, Animator = full pipeline.
    """

    permission_classes = [AllowAny]  # Allow public for calculator exploration

    def post(self, request):
        serializer = VisualMathRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = VisualMathService()

        # Run the async solve in a sync view
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            service.solve(
                user_input=serializer.validated_data["user_input"],
                mode=serializer.validated_data.get("mode", "auto"),
                output_mode=serializer.validated_data.get("output_mode", "video"),
                quality=serializer.validated_data.get("quality", "medium"),
                language=serializer.validated_data.get("language", "en"),
                image_base64=serializer.validated_data.get("image_base64", ""),
            )
        )

        # If this is a geogebra success, optionally save the sketch
        if result.get("type") == "geogebra" and result.get("commands"):
            profile = get_user_profile(request)
            if profile:
                sketch = GeoGebraSketch.objects.create(
                    creator=profile,
                    title=serializer.validated_data["user_input"][:80],
                    source="expression",
                    expression=serializer.validated_data["user_input"],
                    ggb_commands="\n".join(result["commands"]),
                )
                result["sketch_id"] = str(sketch.id)

        # If this is an animation, return the project_id for polling
        if result.get("type") == "animate":
            result["polling_url"] = (
                f"/api/v1/visual-math/animations/{result.get('project_id')}/status/"
            )

        logger.info(
            f"VisualMathSolve: type={result.get('type')} "
            f"input={serializer.validated_data['user_input'][:40]}"
        )

        return Response(result)


# ─── Animation Status Polling ──────────────────────────────────────────

class AnimationStatusView(APIView):
    """
    GET /api/v1/visual-math/animations/<uuid>/status/

    Poll the current status of an animation project.
    Used by the frontend to track rendering progress.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk):
        service = VisualMathService()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            service.animator.get_project_status(str(pk))
        )

        if not result.get("success"):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result)


# ─── GeoGebra Sketch CRUD ──────────────────────────────────────────────

class GeoGebraSketchViewSet(viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /api/v1/visual-math/sketches/

    CRUD for GeoGebra sketches.
    """

    serializer_class = GeoGebraSketchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return GeoGebraSketch.objects.all().order_by("-updated_at")

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        if profile:
            serializer.save(creator=profile)


# ─── Animation Project CRUD ───────────────────────────────────────────

class AnimationProjectViewSet(viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /api/v1/visual-math/animations/

    CRUD for animation projects.
    """

    serializer_class = AnimationProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return AnimationProject.objects.all().order_by("-updated_at")

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        if profile:
            serializer.save(creator=profile)