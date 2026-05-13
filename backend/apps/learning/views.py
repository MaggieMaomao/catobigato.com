"""Learning app views — stub endpoints for Phase 1."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class NotesStubView(APIView):
    """GET /api/v1/learning/notes/ — placeholder."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Notes API — coming in Phase 2", "status": "planned"})


class QuestionsStubView(APIView):
    """GET /api/v1/learning/questions/ — placeholder."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Questions API — coming in Phase 2", "status": "planned"})


class QuestionSetsStubView(APIView):
    """GET /api/v1/learning/question-sets/ — placeholder."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Question Sets API — coming in Phase 2", "status": "planned"})


class ExamsStubView(APIView):
    """GET /api/v1/learning/exams/ — placeholder."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Exams API — coming in Phase 2", "status": "planned"})