
from typing import Dict, Any
import re

from app.agents.email_agent.tools.gmail_reader import (
    get_unread_emails,
    get_important_emails,
)
from app.services.llm_service import get_llm
from app.agents.email_agent.tools.gmail_sender import send_email



def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool node with STRICT graph contracts.

    GUARANTEES:
    - tool_result is ALWAYS a dict
    - _next is ALWAYS set
    - deadline_node will NEVER crash
    - summarize latest / next ALWAYS works
    """

    llm = get_llm()

    user_input: str = state["user_input"]
    intent = state.get("intent")

    context = state.get("context", {})
    text = user_input.lower()


    # -------------------------------------------------
    # 📤 SEND EMAIL (ONLY AFTER CONFIRMATION)
    # -------------------------------------------------
    if state.get("email_status") == "ready_to_send":

        payload = state.get("draft_email")

        if not payload:
            state["response"] = "No draft email found to send."
            state["tool_result"] = {}
            state["_next"] = "__end__"
            return state

        result = send_email(payload=payload)

        state["tool_result"] = result

        state["response"] = (
            f"✅ Email successfully sent to {payload.get('to')}."
        )

        # 🔥 CLEAR DRAFT AFTER SENDING
        state["tool_name"] = None
        state["tool_input"] = None
        state["draft_email"] = None
        state["pending_action"] = None
        state["email_status"] = None

        state["_next"] = "final"
        return state




    # -------------------------------------------------
    # 🔥 SUMMARY: MOST RECENT / NEXT IMPORTANT EMAIL
    # -------------------------------------------------
    if "summarize" in text:

        # Determine cursor
        if "next" in text:
            cursor = context.get("cursor", 0) + 1
        else:
            cursor = 0  # most recent / latest

        emails = context.get("emails")

        # Fallback fetch
        if not emails:
            emails = get_important_emails(limit=10)

        if not emails or cursor >= len(emails):
            state["response"] = "There are no more important emails to summarize."
            state["tool_result"] = {}   # ✅ ALWAYS SET
            state["_next"] = "__end__"
            return state

        email = emails[cursor]

        prompt = f"""
Summarize this email briefly (2–3 sentences).
Focus on the key message and any required action.

Subject: {email.get('subject')}
From: {email.get('from')}
Body: {email.get('body', '')[:500]}
"""

        summary = llm.invoke(prompt).content.strip()

        state["response"] = summary

        # ✅ CRITICAL: ALWAYS PROVIDE tool_result
        state["tool_result"] = {
            "summary": summary
        }

        state["context"] = {
            "emails": emails,
            "last_type": "important",
            "cursor": cursor
        }

        state["_next"] = "__end__"
        return state

    # -------------------------------------------------
    # UNREAD EMAIL COUNT
    # -------------------------------------------------
    if intent == "unread_count":
        match = re.search(r"(\d+)\s*day", user_input.lower())
        days = int(match.group(1)) if match else None

        unread_count = get_unread_emails(
            days=days
        )

        state["tool_result"] = {
            "unread_count": unread_count,
            "days": days,
        }

        # -------------------------------
        # LLM PROMPT (STRICT)
        # -------------------------------
        prompt = f"""
    You are generating a factual response for an email assistant.

    Facts (do not change):
    - Unread email count: {unread_count}
    - Time window (days): {days if days else "ALL TIME"}

    Rules:
    - Answer using ONLY the facts above.
    - Do NOT add or remove conditions.
    - Do NOT guess or generalize.
    - If a time window is provided, mention it explicitly.
    - Keep the response to one sentence.

    Now generate the response.
    """

        state["response"] = llm.invoke(prompt).content.strip()
        state["_next"] = "__end__"
        return state


    # -------------------------------------------------
    # IMPORTANT EMAIL COUNT
    # -------------------------------------------------
    if intent == "important_count":
        emails = get_important_emails(limit=10)
        count = len(emails)

        state["tool_result"] = {
            "important_count": count,
            "emails": emails
        }

        state["context"] = {
            "last_type": "important",
            "emails": emails,
            "cursor": -1
        }

        prompt = f"""
Important emails found: {count}

Respond in ONE short sentence.
Say: "You have X important emails."
Replace X with the number.
Do NOT add extra commentary.

"""

        state["response"] = llm.invoke(prompt).content.strip()
        state["_next"] = "__end__"
        return state

    # -------------------------------------------------
    # FALLBACK (SAFE)
    # -------------------------------------------------
    state["response"] = (
        "I can help with unread emails, important emails, "
        "or summarize the latest or next one."
    )
    state["tool_result"] = {}   # ✅ ALWAYS SET
    state["_next"] = "__end__"
    return state
