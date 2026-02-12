from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import traceback
import copy

from app.agents.email_agent.graph import run_email_agent
from app.core.database import SessionLocal
from app.models.db_models import AgentConversation

router = APIRouter()


# -----------------------------
# Request Model
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    updated_draft: Optional[Dict[str, Any]] = None


# -----------------------------
# Response Model
# -----------------------------
class ChatResponse(BaseModel):
    response: str
    session_id: str
    raw_state: Dict[str, Any]


# -----------------------------
# Chat Endpoint
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print("🔥 NEW REQUEST:", request.message)

    db = SessionLocal()
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # ------------------------------------------
        # 🔥 Load previous state from DB (CRITICAL)
        # ------------------------------------------
        last_record = (
            db.query(AgentConversation)
            .filter(AgentConversation.conversation_id == session_id)
            .order_by(AgentConversation.created_at.desc())
            .first()
        )

        if last_record and last_record.agent_state:
            state = copy.deepcopy(last_record.agent_state)

            # IMPORTANT: reset previous response so it doesn't short-circuit
            state["response"] = None
            state["intent"] = None   # 🔥 ADD THIS
            # Update user input
            state["user_input"] = request.message
            state["updated_draft"] = request.updated_draft

        else:
            state = {
                "session_id": session_id,
                "user_input": request.message,
                "intent": None,
                "tool_name": None,
                "tool_input": None,
                "tool_result": {},
                "pending_action": None,
                "deadlines": [],
                "tasks": [],
                "response": None,
                "messages": [],
                "updated_draft": request.updated_draft,

            }

        # ------------------------------------------
        # Run agent
        # ------------------------------------------
        final_state = run_email_agent(state)

        if not isinstance(final_state, dict):
            raise ValueError("Agent did not return a dictionary state.")

        response_text = final_state.get("response") or "No response generated."

        # ------------------------------------------
        # Save updated state back to DB
        # ------------------------------------------
        conversation = AgentConversation(
            conversation_id=session_id,
            user_input=request.message,
            assistant_response=response_text,
            agent_state=final_state,
        )
        db.add(conversation)
        db.commit()

        print("FINAL RESPONSE:", response_text)


        return ChatResponse(
            response=response_text,
            session_id=session_id,
            raw_state=final_state,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )
    finally:
        db.close()


# -----------------------------
# History Endpoint
# -----------------------------
@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    db = SessionLocal()
    try:
        records: List[AgentConversation] = (
            db.query(AgentConversation)
            .filter(AgentConversation.conversation_id == session_id)
            .order_by(AgentConversation.created_at.asc())
            .all()
        )

        history = [
            {
                "user_input": r.user_input,
                "assistant_response": r.assistant_response,
                "created_at": r.created_at,
            }
            for r in records
        ]

        return {"session_id": session_id, "history": history}

    finally:
        db.close()
