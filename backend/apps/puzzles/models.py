"""Puzzles app models — Puzzle bank, sources, crawlers."""

import uuid
from django.db import models


class PuzzleSource(models.Model):
    """
    Source of puzzles — manual creation, crawler, or import.
    Tracks origin for copyright and quality management.
    """

    SOURCE_TYPE_CHOICES = [
        ("manual", "Manual Creation"),
        ("crawler", "Web Crawler"),
        ("import", "File Import"),
        ("ai_generated", "AI Generated"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    source_type = models.CharField(
        max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual"
    )
    source_url = models.URLField(max_length=500, blank=True)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="puzzle_sources",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Source-specific metadata (e.g., crawl date, import file)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "puzzle_sources"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class Puzzle(models.Model):
    """
    Individual puzzle — problems, brain teasers, curriculum-aligned questions.
    """

    TYPE_CHOICES = [
        ("mcq", "Multiple Choice"),
        ("short_answer", "Short Answer"),
        ("long_answer", "Long Answer"),
        ("problem_solving", "Problem Solving"),
        ("proof", "Proof"),
        ("coding", "Coding Challenge"),
        ("puzzle", "Logic Puzzle"),
    ]
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ]
    SUBJECT_CHOICES = [
        ("math", "Mathematics"),
        ("physics", "Physics"),
        ("chemistry", "Chemistry"),
        ("biology", "Biology"),
        ("literacy", "Literacy"),
        ("arts", "Arts"),
        ("logic", "Logic"),
        ("general", "General"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        PuzzleSource,
        on_delete=models.SET_NULL,
        null=True,
        related_name="puzzles",
    )
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="puzzles_created",
    )

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default="beginner"
    )

    # Content
    content = models.JSONField(
        default=dict,
        help_text="Block-based puzzle content"
    )
    solution = models.JSONField(
        default=dict,
        help_text="Solution with steps"
    )
    hints = models.JSONField(default=list)
    tags = models.JSONField(default=list)

    # Curriculum mapping
    curriculum_references = models.JSONField(
        default=list,
        help_text="[{'region': 'Canada-ON', 'grade': '10', 'strand': 'Algebra'}]"
    )

    # Stats
    times_used = models.IntegerField(default=0)
    times_solved = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

    # Status
    status = models.CharField(
        max_length=20, choices=PuzzleSource.STATUS_CHOICES, default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "puzzles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.subject}/{self.difficulty}]"