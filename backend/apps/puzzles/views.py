"""Puzzles app views — stub endpoints for Phase 1."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class PuzzlesStubView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Puzzles API — coming in Phase 4", "status": "planned"})


class PuzzleSourcesStubView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Puzzle Sources API — coming in Phase 4", "status": "planned"})