"""Calculator app serializers."""

from rest_framework import serializers
from .models import CustomFunction, CalculationHistory


class CustomFunctionSerializer(serializers.ModelSerializer):
    """Serializer for custom user-defined functions."""

    class Meta:
        model = CustomFunction
        fields = [
            "id", "name", "description", "definition",
            "is_public", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomFunctionCreateSerializer(serializers.Serializer):
    """Serializer for creating a custom function."""
    name = serializers.CharField(max_length=64)
    description = serializers.CharField(max_length=500, required=False, default="")
    definition = serializers.JSONField()
    is_public = serializers.BooleanField(default=False)

    def validate_definition(self, value):
        if "params" not in value or "body" not in value:
            raise serializers.ValidationError(
                "definition must contain 'params' and 'body'"
            )
        if not isinstance(value["params"], list):
            raise serializers.ValidationError("params must be a list")
        if not isinstance(value["body"], str) or not value["body"].strip():
            raise serializers.ValidationError("body must be a non-empty string")
        return value


class EvaluateRequestSerializer(serializers.Serializer):
    """Serializer for evaluation requests."""
    expression = serializers.CharField()
    variables = serializers.DictField(required=False, default=dict)
    mode = serializers.ChoiceField(
        choices=["basic", "scientific", "trigonometric", "algebra", "calculus", "graph"],
        default="basic"
    )
    precision = serializers.IntegerField(default=10, min_value=1, max_value=15)


class PlotRequestSerializer(serializers.Serializer):
    """Serializer for plot requests."""
    expression = serializers.CharField()
    variable = serializers.CharField(default="x")
    x_range = serializers.ListField(min_length=2, max_length=2, required=False, default=[-10, 10])
    y_range = serializers.ListField(min_length=2, max_length=2, required=False, default=[-10, 10])
    num_points = serializers.IntegerField(default=500, min_value=10, max_value=2000)


class DerivativeRequestSerializer(serializers.Serializer):
    """Serializer for derivative requests."""
    expression = serializers.CharField()
    variable = serializers.CharField(default="x")
    order = serializers.IntegerField(default=1, min_value=1, max_value=5)


class IntegralRequestSerializer(serializers.Serializer):
    """Serializer for integral requests."""
    expression = serializers.CharField()
    variable = serializers.CharField(default="x")
    lower = serializers.FloatField(required=False)
    upper = serializers.FloatField(required=False)


class SolveRequestSerializer(serializers.Serializer):
    """Serializer for equation solving requests."""
    equation = serializers.CharField()
    variable = serializers.CharField(default="x")


class CalculationHistorySerializer(serializers.ModelSerializer):
    """Serializer for calculation history."""

    class Meta:
        model = CalculationHistory
        fields = [
            "id", "mode", "expression", "result", "inputs",
            "metadata", "created_at"
        ]
        read_only_fields = ["id", "created_at"]