
from typing import Dict, Any


def final_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final response builder.
    Responsible for:
    - Greeting
    - Unread count
    - Important email confirmation
    - Important email summary
    - Email sent confirmation
    - Fallback response
    """

    # -------------------------------------------------
    # If response already prepared (e.g., cancel flow)
    # -------------------------------------------------
    if state.get("response"):
        return state

    intent = state.get("intent")
    tool_result = state.get("tool_result") or {}
    user_input = state.get("user_input", "").strip().lower()

    # -------------------------------------------------
    # Greeting
    # -------------------------------------------------
    if user_input in {"hi", "hello", "hey"}:
        state["response"] = "Hey 👋 How can I help with your emails today?"
        return state

    # -------------------------------------------------
    # Unread Count
    # -------------------------------------------------
    if intent == "unread_count":
        count = tool_result.get("unread_count", 0)
        state["response"] = f"You have {count} unread emails."
        return state

    # -------------------------------------------------
    # Important Count (Ask for Confirmation)
    # -------------------------------------------------
    if intent == "important_count" and "summary" not in tool_result:
        count = tool_result.get("important_count", 0)

        if count == 0:
            state["response"] = "You have no important emails."
            return state

        state["pending_action"] = "CONFIRM_SUMMARY"
        state["response"] = (
            f"You have {count} important emails.\n"
            "Do you want me to summarize them?"
        )
        return state

    # -------------------------------------------------
    # Important Summary (After Confirmation)
    # -------------------------------------------------
    if tool_result and "summary" in tool_result:
        summary = tool_result.get("summary", "")
        deadlines = state.get("deadlines", []) or []
        tasks = state.get("tasks", []) or []

        message = f"📩 Summary:\n{summary}\n\n"

        if deadlines:
            message += "⏳ Deadlines:\n"
            for d in deadlines:
                message += f"- {d.get('description')} (Due: {d.get('due_date')})\n"
            message += "\n"

        if tasks:
            message += "📌 Tasks:\n"
            for t in tasks:
                message += f"- {t.get('task')} (Due: {t.get('due_date')})\n"

        state["response"] = message.strip()

        # 🔥 CRITICAL: Clear pending state after summary
        state["pending_action"] = None
        state["tool_input"] = None
        state["tool_result"] = None

        return state

    # -------------------------------------------------
    # Email Sent Confirmation
    # -------------------------------------------------
    if tool_result.get("status") in {"sent", "success"}:
        state["response"] = "✅ Your email has been sent successfully."

        # 🔥 CRITICAL: Clear state after send
        state["pending_action"] = None
        state["tool_input"] = None
        state["tool_result"] = None

        return state

    # -------------------------------------------------
    # Fallback
    # -------------------------------------------------
    state["response"] = (
        "I'm not sure how to help with that.\n"
        "You can ask me to check unread emails, "
        "check important emails, or send an email."
    )

    return state
