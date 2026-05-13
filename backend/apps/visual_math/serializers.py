"""VisualMath app serializers."""

from rest_framework import serializers
from .models import GeoGebraSketch, AnimationProject


class VisualMathRequestSerializer(serializers.Serializer):
    """Unified request serializer for visual math requests."""

    user_input = serializers.CharField(
        help_text="Math expression, question, or animation request"
    )
    mode = serializers.ChoiceField(
        choices=["auto", "latex", "geogebra", "animate"],
        default="auto",
        required=False,
    )
    output_mode = serializers.ChoiceField(
        choices=["video", "image"],
        default="video",
        required=False,
    )
    quality = serializers.ChoiceField(
        choices=["low", "medium", "high"],
        default="medium",
        required=False,
    )
    language = serializers.ChoiceField(
        choices=["en", "zh"],
        default="en",
        required=False,
    )
    image_base64 = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Base64-encoded image for GeoGebra analysis (Phase 2)",
    )


class GeoGebraSketchSerializer(serializers.ModelSerializer):
    """Serializer for GeoGebraSketch model."""

    class Meta:
        model = GeoGebraSketch
        fields = [
            "id", "title", "description", "source", "expression",
            "ggb_commands", "image_data", "bbox_elements",
            "constraints", "geometric_relations", "is_shared",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "creator", "created_at", "updated_at"]


class AnimationProjectSerializer(serializers.ModelSerializer):
    """Serializer for AnimationProject model."""

    class Meta:
        model = AnimationProject
        fields = [
            "id", "title", "description", "user_input",
            "concept_analysis", "scene_design", "generated_code",
            "rendered_output_url", "output_mode", "quality",
            "status", "error_message", "celery_task_id",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "creator", "status", "error_message",
            "celery_task_id", "created_at", "updated_at",
        ]


class AnimationStatusSerializer(serializers.Serializer):
    """Serializer for animation status polling response."""

    project_id = serializers.UUIDField()
    status = serializers.CharField()
    rendered_output_url = serializers.URLField(allow_blank=True)
    error_message = serializers.CharField(allow_blank=True)
    message = serializers.CharField(required=False)