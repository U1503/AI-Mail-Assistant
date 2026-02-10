import json
from typing import Dict, Any, List

from app.services.llm_service import get_llm


llm = get_llm()


def deadline_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract deadlines from summarized important emails.
    """

    tool_result = state.get("tool_result", {})
    summary = tool_result.get("summary")

    # If no summary exists, skip
    if not summary:
        state["deadlines"] = []
        return state

    prompt = f"""
Extract ALL deadlines from the following summary.

Rules:
- A deadline can be a date, day, or time.
- If date cannot be determined, set due_date to null.
- Do NOT invent deadlines.
- Return ONLY valid JSON.

Format:
[
  {{
    "description": "task description",
    "due_date": "YYYY-MM-DD" | null
  }}
]

Summary:
{summary}
"""

    try:
        response = llm.invoke(prompt).content.strip()
        deadlines: List[Dict[str, Any]] = json.loads(response)

        if isinstance(deadlines, list):
            state["deadlines"] = deadlines
        else:
            state["deadlines"] = []

    except Exception:
        state["deadlines"] = []

    return state
