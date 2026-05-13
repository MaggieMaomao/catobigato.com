"""Learning app models — Notes, QuestionSets, Exams, Attempts."""

import uuid
from django.db import models


class Note(models.Model):
    """User-created notes with block-based content."""

    SUBJECT_CHOICES = [
        ("math", "Mathematics"),
        ("physics", "Physics"),
        ("chemistry", "Chemistry"),
        ("biology", "Biology"),
        ("literacy", "Literacy"),
        ("arts", "Arts"),
        ("general", "General"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="notes",
    )
    title = models.CharField(max_length=255)
    content = models.JSONField(
        default=dict,
        help_text="Block-based content: {blocks: [{type, data}]}"
    )
    subject = models.CharField(
        max_length=20, choices=SUBJECT_CHOICES, default="general"
    )
    tags = models.JSONField(default=list)  # ["algebra", "quadratic"]
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notes"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.subject})"


class Question(models.Model):
    """
    Polymorphic question model.
    Supports MCQ, numeric, proof, code, simulation types.
    """

    TYPE_CHOICES = [
        ("mcq", "Multiple Choice"),
        ("numeric", "Numeric Answer"),
        ("proof", "Proof/ Derivation"),
        ("code", "Code"),
        ("simulation", "Simulation"),
    ]
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]
    SUBJECT_CHOICES = [
        ("math", "Mathematics"),
        ("physics", "Physics"),
        ("chemistry", "Chemistry"),
        ("biology", "Biology"),
        ("literacy", "Literacy"),
        ("arts", "Arts"),
        ("general", "General"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default="medium"
    )
    content = models.JSONField(
        default=dict,
        help_text="Block-based question content"
    )
    answer = models.JSONField(
        default=dict,
        help_text="Correct answer(s), possibly with grading rubric"
    )
    hints = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    explanation = models.JSONField(
        default=dict,
        help_text="Post-submission explanation"
    )
    is_public = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.subject}/{self.difficulty}] {self.id}"


class QuestionSet(models.Model):
    """Collection of questions for practice or exam."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="question_sets",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(
        "Question", related_name="question_sets", blank=True
    )
    subject = models.CharField(max_length=20, default="general")
    difficulty = models.CharField(max_length=10, default="medium")
    time_limit = models.IntegerField(
        default=0, help_text="Time limit in minutes, 0 = unlimited"
    )
    is_exam = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question_sets"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ExamAttempt(models.Model):
    """Student's attempt at an exam or practice set."""

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("graded", "Graded"),
        ("reviewed", "Reviewed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="exam_attempts",
    )
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    answers = models.JSONField(
        default=dict,
        help_text="Student's answers: {question_id: answer}"
    )
    score = models.FloatField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="in_progress"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "exam_attempts"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student} - {self.question_set.title} ({self.status})"


class StudyGroup(models.Model):
    """Study groups for collaborative learning."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=20, default="general")
    creator = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        related_name="groups_created",
    )
    members = models.ManyToManyField(
        "accounts.UserProfile",
        related_name="groups_joined",
        through="StudyGroupMembership",
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "study_groups"

    def __str__(self):
        return self.name


class StudyGroupMembership(models.Model):
    """Through table for study group membership."""

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "study_group_memberships"
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user} in {self.group} ({self.role})"