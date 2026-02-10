# from typing import Dict, Any


# def router_node(state: Dict[str, Any]) -> Dict[str, Any]:

#     pending = (state.get("pending_action") or "").strip()
#     user_input = state.get("user_input", "").strip().lower()
#     intent = state.get("intent")

#     # -------------------------------------------------
#     # HANDLE CONFIRMATION ONLY IF INTENT IS NONE
#     # -------------------------------------------------
#     if pending and intent is None:

#         if pending == "CONFIRM_SEND":

#             if user_input in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
#                 state["_next"] = "tool"
#                 return state

#             state["response"] = "Okay, I won't send the email."
#             state["pending_action"] = None
#             state["tool_input"] = None
#             state["tool_result"] = None
#             state["_next"] = "final"
#             return state

#         if pending == "CONFIRM_SUMMARY":

#             if user_input in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
#                 state["_next"] = "tool"
#                 return state

#             state["response"] = "Okay, I won't summarize the emails."
#             state["pending_action"] = None
#             state["tool_input"] = None
#             state["tool_result"] = None
#             state["_next"] = "final"
#             return state
        
#     # -------------------------------------------------
#     # Auto-cancel if user asks something new
#     # -------------------------------------------------
#     if pending and intent not in {None, "send_email"}:
#         print("DEBUG: Auto-cancelling pending action due to new intent")
#         state["pending_action"] = None
#         state["tool_input"] = None
#         state["tool_result"] = None
#         state["response"] = None   # 🔥 ADD THIS
#         pending = None



#     # -------------------------------------------------
#     # NORMAL ROUTING
#     # -------------------------------------------------
#     if intent in {"unread_count", "important_count"}:
#         state["_next"] = "tool"
#         return state

#     if intent == "send_email":
#         state["_next"] = "final"
#         return state

#     state["_next"] = "final"
#     return state


from typing import Dict, Any


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    pending = (state.get("pending_action") or "").strip()
    user_input = state.get("user_input", "").strip().lower()
    intent = state.get("intent")

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
    # 🔥 CONFIRM SUMMARY
    # -------------------------------------------------
    if pending == "CONFIRM_SUMMARY":

        if user_input in {"yes", "yes!", "yes please", "sure", "ok", "okay"}:
            state["_next"] = "tool"
            return state

        if user_input in {"no", "nope", "cancel"}:
            state["response"] = "Okay, I won't summarize the emails."
            state["pending_action"] = None
            state["tool_input"] = None
            state["tool_result"] = None
            state["_next"] = "final"
            return state

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
