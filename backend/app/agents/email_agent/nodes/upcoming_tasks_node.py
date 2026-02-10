from typing import Dict, Any, List


def upcoming_tasks_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert extracted deadlines into structured tasks.
    """

    deadlines = state.get("deadlines", [])
    tasks: List[Dict[str, Any]] = []

    for deadline in deadlines:
        description = deadline.get("description")
        due_date = deadline.get("due_date")

        if not description:
            continue

        tasks.append({
            "task": description,
            "due_date": due_date,
        })

    state["tasks"] = tasks
    return state
