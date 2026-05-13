"""VisualMath app URL routing."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "visual_math"

router = DefaultRouter()
router.register("sketches", views.GeoGebraSketchViewSet, basename="sketch")
router.register("animations", views.AnimationProjectViewSet, basename="animation")

urlpatterns = [
    # Main unified solve endpoint
    path("solve/", views.VisualMathSolveView.as_view(), name="solve"),

    # Animation status polling
    path("animations/<uuid:pk>/status/", views.AnimationStatusView.as_view(), name="animation-status"),

    # Router URLs (sketches and animations CRUD)
    path("", include(router.urls)),
]