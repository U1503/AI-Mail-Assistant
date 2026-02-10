# backend/app/memory/db_memory.py

from typing import Optional, List, Union

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.db_models import AgentConversation
from app.agents.email_agent.state import EmailAgentState


class DBMemory:
    """
    Database-backed memory for the Email Agent.

    Handles persistence regardless of whether
    state is a Pydantic model or a dict (LangGraph output).
    """

    def __init__(self):
        self._Session = SessionLocal

    # -------------------------------------------------
    # Internal helper
    # -------------------------------------------------
    def _normalize_state(
        self,
        state: Union[EmailAgentState, dict],
    ) -> EmailAgentState:
        """
        Ensure we always work with EmailAgentState.
        """
        if isinstance(state, EmailAgentState):
            return state

        if isinstance(state, dict):
            return EmailAgentState(**state)

        raise TypeError("Unsupported state type")

    # -------------------------------------------------
    # Save a single conversation turn
    # -------------------------------------------------
    def save_turn(
        self,
        conversation_id: str,
        state: Union[EmailAgentState, dict],
    ) -> None:
        """
        Persist one agent turn to the database.
        """

        normalized_state = self._normalize_state(state)

        db: Session = self._Session()
        try:
            record = AgentConversation(
                conversation_id=conversation_id,
                user_input=normalized_state.user_input,
                assistant_response=normalized_state.final_response,
                agent_state=normalized_state.model_dump(),
            )

            db.add(record)
            db.commit()
        finally:
            db.close()

    # -------------------------------------------------
    # Load conversation history
    # -------------------------------------------------
    def load_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[AgentConversation]:
        """
        Load recent conversation history.
        """

        db: Session = self._Session()
        try:
            return (
                db.query(AgentConversation)
                .filter(
                    AgentConversation.conversation_id == conversation_id
                )
                .order_by(AgentConversation.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    # -------------------------------------------------
    # Load last agent state
    # -------------------------------------------------
    def load_last_state(
        self,
        conversation_id: str,
    ) -> Optional[EmailAgentState]:
        """
        Load most recent agent state for continuation.
        """

        db: Session = self._Session()
        try:
            record = (
                db.query(AgentConversation)
                .filter(
                    AgentConversation.conversation_id == conversation_id
                )
                .order_by(AgentConversation.created_at.desc())
                .first()
            )

            if not record or not record.agent_state:
                return None

            return EmailAgentState(**record.agent_state)

        finally:
            db.close()
