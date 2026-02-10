# backend/app/models/schemas.py

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """
    API request schema.
    """
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation/session id"
    )
    message: str = Field(..., description="User input message")


class ChatResponse(BaseModel):
    """
    API response schema.
    """
    conversation_id: Optional[str]
    response: str
