"""Social app views — stub endpoints for Phase 1."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class ConversationsStubView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Conversations API — coming in Phase 5", "status": "planned"})


class MessagesStubView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Messages API — coming in Phase 5", "status": "planned"})