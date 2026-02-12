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
    # New3️⃣ SEND EMAIL (Draft / Rewrite / Confirm)
    # -------------------------------------------------
    if intent == "send_email" or pending == "CONFIRM_SEND":

        lowered = user_input.lower()

        # ---------------------------------------------
        # HANDLE CONFIRMATION
        # ---------------------------------------------
        if pending == "CONFIRM_SEND":

            if lowered in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
                print("DEBUG: Final confirmation to send")
                state["email_status"] = "ready_to_send"
                state["_next"] = "router"
                return state

            if lowered in {"no", "nope", "cancel", "no thanks"}:
                print("DEBUG: Draft cancelled")
                state["response"] = "Okay, I won't send the email."
                state["pending_action"] = None
                state["draft_email"] = None
                state["email_status"] = None
                state["_next"] = "final"
                return state

            # -----------------------------------------
            # REWRITE REQUEST
            # -----------------------------------------
            print("DEBUG: Rewriting existing draft")

            existing_draft = state.get("draft_email") or {}

            rewrite_prompt = f"""
                You previously drafted this email:

                To: {existing_draft.get("to")}
                Subject: {existing_draft.get("subject")}
                Body:
                {existing_draft.get("body")}

                User modification request:
                {user_input}

                Rewrite the subject and body accordingly.

                IMPORTANT:
                - Preserve paragraph formatting.
                - Keep greetings and closings on separate lines.
                - Maintain line breaks.
                - Use \\n for new lines inside the JSON body.
                - Do NOT compress everything into one single paragraph.

                Return ONLY valid JSON:
                {{
                "subject": "...",
                "body": "..."
                }}
            """


            response = llm.invoke(rewrite_prompt)
            raw_output = response.content.strip()

            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if not json_match:
                state["response"] = "I couldn't rewrite the email properly. Please try again."
                state["_next"] = "final"
                return state

            try:
                data = json.loads(json_match.group(0))
            except Exception:
                state["response"] = "Error rewriting email. Please try again."
                state["_next"] = "final"
                return state

            # Update draft
            existing_draft["subject"] = data.get("subject", existing_draft.get("subject"))
            existing_draft["body"] = data.get("body", existing_draft.get("body"))

            state["draft_email"] = existing_draft
            state["pending_action"] = "CONFIRM_SEND"

            state["response"] = (
                f"I've updated your draft.\n\n"
                f"To: {existing_draft.get('to')}\n\n"
                f"Subject: {existing_draft.get('subject')}\n\n"
                f"Body:\n{existing_draft.get('body')}\n\n"
                "Do you want me to send it?"
            )

            state["_next"] = "final"
            return state

        # ---------------------------------------------
        # INITIAL DRAFT GENERATION
        # ---------------------------------------------
        prompt = f"""
            Extract email details from the request.

            IMPORTANT:
            - Format the email body in proper paragraphs.
            - Keep greeting and closing on separate lines.
            - Use \\n for line breaks.
            - Do NOT compress into a single paragraph.

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
            state["response"] = "I couldn't understand the email details."
            state["_next"] = "final"
            return state

        try:
            data = json.loads(json_match.group(0))
        except Exception:
            state["response"] = "I couldn't parse the email details properly."
            state["_next"] = "final"
            return state

        recipient = data.get("to", "").strip()
        if not recipient:
            state["response"] = "Please specify a valid recipient email address."
            state["_next"] = "final"
            return state

        valid_list = validate_emails([recipient], check_mx=False)
        if not valid_list:
            state["response"] = "Please provide a valid recipient email address."
            state["_next"] = "final"
            return state

        subject = data.get("subject") or "No Subject"
        body = data.get("body")

        if not body:
            state["response"] = "Please provide email content."
            state["_next"] = "final"
            return state

        draft = {
            "to": recipient,
            "subject": subject,
            "body": body,
        }

        state["draft_email"] = draft
        state["tool_name"] = "SEND_EMAIL"
        state["pending_action"] = "CONFIRM_SEND"
        state["email_status"] = "awaiting_confirmation"

        state["response"] = (
            f"I've drafted your email.\n\n"
            f"To: {recipient}\n\n"
            f"Subject: {subject}\n\n"
            f"Body:\n{body}\n\n"
            "Do you want me to send it?"
        )

        state["_next"] = "final"
        return state


    # -------------------------------------------------
    # 4️⃣ OTHER INTENTS (normal flow)
    # -------------------------------------------------
    return state
