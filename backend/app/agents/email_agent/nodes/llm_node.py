
import json
import re
from typing import Dict, Any

from app.services.llm_service import get_llm
from app.agents.email_agent.utils.intent_rules import detect_intent
from app.agents.email_agent.tools.email_validator import validate_emails

llm = get_llm()


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state["user_input"].strip()
    print("DEBUG: LLM node entered") # for debug

    pending = state.get("pending_action")
    existing_draft = state.get("tool_input", {}) or {}

    # -------------------------------------------------
    # 1️⃣ HANDLE CONFIRMATION (yes / no)
    # -------------------------------------------------
    # if pending in {"CONFIRM_SEND", "CONFIRM_SUMMARY"}:
    if pending == "CONFIRM_SEND":
        lowered = user_input.lower()

        if lowered in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
            print("DEBUG: Confirmation detected")
            state["_next"] = "router"
            return state

        if lowered in {"no", "nope", "cancel", "no thanks"}:
            print("DEBUG: Cancellation detected")
            state["_next"] = "router"
            return state

        print("DEBUG: Continuing draft editing")

    # -------------------------------------------------
    # 2️⃣ Intent Detection
    # -------------------------------------------------
    intent = detect_intent(user_input)
    print("DEBUG INTENT:", intent)


    if not intent:
        prompt = f"""
Classify into ONE:
- unread_count
- important_count
- send_email
- unknown

User: {user_input}
Return only the intent.
"""
        response = llm.invoke(prompt)
        intent = response.content.strip().lower()
    # 🔥 CRITICAL SAFETY FIX
    if not intent:
        intent = "unknown"
    # 🔥 SAFE OVERRIDE FOR SEND MAIL
    text = user_input.lower()
    if intent == "unknown":
        if "send" in text and ("mail" in text or "email" in text):
            intent = "send_email"

    state["intent"] = intent

    # -------------------------------------------------
    # 3️⃣ SEND EMAIL (Draft / Continue Draft)
    # -------------------------------------------------
    if intent == "send_email" or pending == "CONFIRM_SEND":

        prompt = f"""
Extract email details from the request.

Return ONLY valid JSON:
{{
  "to": "...",
  "subject": "...",
  "body": "..."
}}

User request:
{user_input}
"""
        response = llm.invoke(prompt)
        raw_output = response.content.strip()

        print("DEBUG: LLM RAW RESPONSE:", raw_output)

        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

        if not json_match:
            state["response"] = (
                "I couldn't understand the email details. "
                "Please rephrase your request."
            )
            state["_next"] = "final"
            return state

        try:
            data = json.loads(json_match.group(0))
        except Exception:
            state["response"] = (
                "I couldn't parse the email details properly. "
                "Please rephrase your request."
            )
            state["_next"] = "final"
            return state

        # Merge with existing draft
        merged = existing_draft.copy()

        for key in ["to", "subject", "body"]:
            value = data.get(key)
            if value:
                merged[key] = value

        print("DEBUG: Merged Draft:", merged)

        # -------------------------------------------------
        # Validate recipient
        # -------------------------------------------------

        recipient = merged.get("to", "").strip()

        if not recipient:
            state["response"] = "Please specify a valid recipient email address."
            state["tool_input"] = merged
            state["_next"] = "final"
            return state

        valid_list = validate_emails([recipient], check_mx=False)

        if not valid_list:
            state["response"] = "Please provide a valid recipient email address."
            state["tool_input"] = merged
            state["_next"] = "final"
            return state

        # Auto-fill subject if missing
        if not merged.get("subject"):
            if merged.get("body"):
                merged["subject"] = merged["body"][:50]
            else:
                merged["subject"] = "No Subject"

        # Validate body
        if not merged.get("body"):
            state["response"] = "Please provide email content."
            state["tool_input"] = merged
            state["_next"] = "final"
            return state

        # Save draft
        state["tool_name"] = "SEND_EMAIL"
        state["tool_input"] = merged
        state["pending_action"] = "CONFIRM_SEND"

        state["response"] = (
            f"I've drafted an email to {merged.get('to')}.\n\n"
            f"Subject: {merged.get('subject')}\n\n"
            "Do you want me to send it?"
        )

        state["_next"] = "final"
        return state

    # -------------------------------------------------
    # 4️⃣ OTHER INTENTS (normal flow)
    # -------------------------------------------------
    return state
