"""Calculator schemas."""

from pydantic import BaseModel
from typing import Optional
import uuid


class CalculateRequest(BaseModel):
    expression: str
    mode: str = "basic"  # basic | scientific | trigonometric | graph


class CalculateResponse(BaseModel):
    result: str
    expression: str
    history_id: Optional[uuid.UUID] = None


class CustomFunctionCreate(BaseModel):
    name: str
    parameters: list[str] = []
    expression: str


class CustomFunctionResponse(BaseModel):
    id: uuid.UUID
    name: str
    parameters: list[str]
    expression: str
    created_at: str

    class Config:
        from_attributes = True


class HistoryEntry(BaseModel):
    id: uuid.UUID
    expression: str
    result: str
    history_type: str
    created_at: str

    class Config:
        from_attributes = True