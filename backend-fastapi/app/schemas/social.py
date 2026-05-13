"""Social schemas."""

from pydantic import BaseModel
import uuid


class ConversationResponse(BaseModel):
    id: uuid.UUID
    last_message_at: str | None = None
    created_at: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True