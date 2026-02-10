# backend/app/agents/email_agent/utils/intent_rules.py

import re
from typing import Optional

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)


def detect_intent(user_input: str) -> Optional[str]:
    """
    Rule-based intent detection.
    Must match router + tool expected intent strings.
    """

    text = user_input.lower()

    # -------------------------------------------------
    # SEND EMAIL
    # -------------------------------------------------
    if EMAIL_REGEX.search(text) and any(
        w in text for w in ["send", "email", "mail", "wish", "greet", "compose"]
    ):
        return "send_email"

    # -------------------------------------------------
    # UNREAD COUNT
    # -------------------------------------------------
    if "unread" in text:
        return "unread_count"

    # -------------------------------------------------
    # IMPORTANT EMAIL
    # -------------------------------------------------
    if "important" in text:
        return "important_count"

    return None
