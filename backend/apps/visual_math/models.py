"""
VisualMath app models — GeoGebra sketches and animation projects.
"""

import uuid
from django.db import models


class GeoGebraSketch(models.Model):
    """
    Stored GeoGebra sketch with GGBScript commands.
    Can be created from an expression or from an image (via VisionSolver).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="geogebra_sketches",
    )

    # Identity
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, max_length=1000)

    # Source
    SOURCE_CHOICES = [
        ("expression", "Math Expression"),
        ("image", "Image Analysis"),
        ("manual", "Manual Editing"),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")

    # The original expression (if source == expression)
    expression = models.TextField(blank=True)

    # The generated GGBScript commands
    ggb_commands = models.TextField(
        blank=True,
        help_text="GeoGebra Classic scripting commands, one per line"
    )

    # Image base64 (stored only if source == image)
    image_data = models.TextField(
        blank=True,
        help_text="Base64-encoded source image (for image-based sketches)"
    )

    # Metadata from vision pipeline
    bbox_elements = models.JSONField(default=list, blank=True)
    constraints = models.JSONField(default=list, blank=True)
    geometric_relations = models.JSONField(default=list, blank=True)

    # Sharing
    is_shared = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "geogebra_sketches"
        ordering = ["-updated_at"]
        verbose_name = "GeoGebra Sketch"
        verbose_name_plural = "GeoGebra Sketches"

    def __str__(self):
        return f"{self.title or 'Untitled Sketch'} ({self.source})"


class AnimationProject(models.Model):
    """
    Math animation project — backed by Manim scene generation.
    Tracks the full pipeline: concept analysis → design → code → render.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="animation_projects",
    )

    # Identity
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=1000)

    # User request
    user_input = models.TextField(
        help_text="Original natural-language request for the animation"
    )

    # Pipeline stages (filled as pipeline runs)
    concept_analysis = models.JSONField(default=dict, blank=True)
    scene_design = models.JSONField(default=dict, blank=True)
    generated_code = models.TextField(blank=True)
    rendered_output_url = models.URLField(max_length=500, blank=True)

    # Render config
    OUTPUT_MODE_CHOICES = [
        ("video", "Video (MP4)"),
        ("image", "Image (PNG)"),
    ]
    output_mode = models.CharField(max_length=10, choices=OUTPUT_MODE_CHOICES, default="video")

    QUALITY_CHOICES = [
        ("low", "Low (fast)"),
        ("medium", "Medium"),
        ("high", "High (slow)"),
    ]
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default="medium")

    # Status
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("analysis", "Concept Analysis"),
        ("design", "Scene Design"),
        ("coding", "Code Generation"),
        ("rendering", "Rendering"),
        ("done", "Completed"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Error message if failed
    error_message = models.TextField(blank=True)

    # Celery task ID for async rendering
    celery_task_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "animation_projects"
        ordering = ["-updated_at"]
        verbose_name = "Animation Project"
        verbose_name_plural = "Animation Projects"

    def __str__(self):
        return f"{self.title} ({self.status})"