# backend/app/models/db_models.py

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.core.database import Base


class AgentConversation(Base):
    """
    Stores conversation-level agent memory.

    One row per conversation turn.
    """

    __tablename__ = "agent_conversations"

    id = Column(Integer, primary_key=True, index=True)

    # Conversation/session identifier
    conversation_id = Column(String, index=True, nullable=False)

    # User input for this turn
    user_input = Column(Text, nullable=False)

    # Assistant final response
    assistant_response = Column(Text, nullable=True)

    # Full agent state snapshot (JSON)
    agent_state = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<AgentConversation "
            f"(conversation_id={self.conversation_id}, "
            f"id={self.id})>"
        )
