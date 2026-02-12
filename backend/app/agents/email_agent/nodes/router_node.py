
from typing import Dict, Any


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:

    # 🔥 STOP IF LLM ALREADY GENERATED A RESPONSE
    if state.get("response") and state.get("pending_action") != "CONFIRM_SEND":
        state["_next"] = "final"
        return state


    pending = (state.get("pending_action") or "").strip()
    user_input = state.get("user_input", "").strip().lower()
    intent = state.get("intent")
    # -------------------------------------------------
    # 🔥 DIRECT SEND AFTER UI UPDATE
    # -------------------------------------------------
    if state.get("email_status") == "ready_to_send":
        state["_next"] = "tool"
        return state


    # -------------------------------------------------
    # 🔥 CONFIRM SEND (HIGHEST PRIORITY)
    # -------------------------------------------------
    if pending == "CONFIRM_SEND":

        if user_input in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
            # confirmation accepted → go to tool
            state["pending_action"] = None 
            state["intent"] = "send_email"   # 🔥 THIS LINE IS REQUIRED
            state["_next"] = "tool"
            return state

        if user_input in {"no", "nope", "cancel"}:
            state["response"] = "Okay, I won't send the email."
            state["pending_action"] = None
            state["tool_input"] = None
            state["tool_result"] = None
            state["tool_name"] = None
            state["_next"] = "final"
            return state

        # still waiting for yes/no
        state["_next"] = "final"
        return state

    # -------------------------------------------------
    # NORMAL ROUTING (NO PENDING ACTION)
    # -------------------------------------------------
    if intent in {"unread_count", "important_count", "send_email"}:
        state["_next"] = "tool"
        return state

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    state["_next"] = "final"
    return state
