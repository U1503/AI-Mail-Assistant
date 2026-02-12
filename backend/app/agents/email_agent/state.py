# backend/app/agents/email_agent/state.py

from typing import TypedDict, Optional, List, Dict, Any


class EmailAgentState(TypedDict):
    # --------------------------------------------------
    # Session
    # --------------------------------------------------
    session_id: str
    user_input: str

    # --------------------------------------------------
    # Intent detection
    # --------------------------------------------------
    intent: Optional[str]

    # --------------------------------------------------
    # Tool execution
    # --------------------------------------------------
    tool_name: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]

    # --------------------------------------------------
    # Multi-step control flow
    # --------------------------------------------------
    pending_action: Optional[str]


    # --------------------------------------------------
    # Email Draft Handling (NEW)
    # --------------------------------------------------
    draft_email: Optional[Dict[str, Any]]  # {"to": "", "subject": "", "body": ""}
    email_status: Optional[str]  # "draft" | "awaiting_confirmation" | "sent"


    # --------------------------------------------------
    # Important email processing
    # --------------------------------------------------
    deadlines: Optional[List[Dict[str, Any]]]
    tasks: Optional[List[Dict[str, Any]]]

    # --------------------------------------------------
    # Final output
    # --------------------------------------------------
    response: Optional[str]

    # --------------------------------------------------
    # Chat memory (for UI)
    # --------------------------------------------------
    messages: List[Dict[str, str]]


# Alias for graph
AgentState = EmailAgentState
