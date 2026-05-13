"""Calculator app models — custom functions and history."""

import uuid
import json
from django.db import models
from django.conf import settings


class CustomFunction(models.Model):
    """
    User-defined calculator functions (Excel-like).
    Users can define f(x, y) = expression, store it, and reuse it.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The user who created this function
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="custom_functions",
    )

    # Function identity
    name = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, max_length=500)

    # Function definition — stored as JSON
    # Example: {"params": [{"name": "x", "type": "number"}, {"name": "y", "type": "number"}], "body": "x^2 + sin(y)"}
    definition = models.JSONField()

    # Visibility
    is_public = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "custom_functions"
        unique_together = ("creator", "name")
        verbose_name = "Custom Function"
        verbose_name_plural = "Custom Functions"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}({', '.join(p['name'] for p in self.definition.get('params', []))})"


class CalculationHistory(models.Model):
    """
    History of user calculations — for reference, redo, analytics.
    """

    MODE_CHOICES = [
        ("basic", "Basic"),
        ("scientific", "Scientific"),
        ("trigonometric", "Trigonometric"),
        ("algebra", "Algebra"),
        ("calculus", "Calculus"),
        ("graph", "Graphing"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="calculation_history",
    )

    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="basic")
    expression = models.TextField()
    result = models.TextField()
    inputs = models.JSONField(default=dict)  # Named variable values
    metadata = models.JSONField(default=dict)  # Extra info (e.g., graph settings)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "calculation_history"
        verbose_name = "Calculation History"
        verbose_name_plural = "Calculation Histories"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.expression} = {self.result}"