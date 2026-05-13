"""
Main URL configuration for CatobiGato.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "ok", "service": "catobigato"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/v1/accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("api/v1/calculator/", include("apps.calculator.urls", namespace="calculator")),
    path("api/v1/learning/", include("apps.learning.urls", namespace="learning")),
    path("api/v1/puzzles/", include("apps.puzzles.urls", namespace="puzzles")),
    path("api/v1/social/", include("apps.social.urls", namespace="social")),
    path("api/v1/visual-math/", include("apps.visual_math.urls", namespace="visual_math")),
]