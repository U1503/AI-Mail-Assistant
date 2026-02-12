
from typing import List, Dict

from app.agents.email_agent.tools.gmail_utils import get_gmail_service
from app.agents.email_agent.tools.raw_email_extractor import extract_email_text

'''
def _fetch_messages(user_id: str, query: str, max_results: int = 10):
    service = get_gmail_service(user_id)

    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    messages = response.get("messages", [])
    results = []

    for msg in messages:
        message = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )
        results.append(message)

    return results
'''

def _structure_email(full_msg) -> Dict[str, str]:
    headers = full_msg.get("payload", {}).get("headers", [])

    subject = ""
    sender = ""

    for h in headers:
        if h["name"].lower() == "subject":
            subject = h["value"]
        if h["name"].lower() == "from":
            sender = h["value"]

    body = extract_email_text([full_msg])
    body_text = body[0] if body else ""

    return {
        "subject": subject,
        "from": sender,
        "body": body_text,
    }


def get_unread_emails(days: int | None = None) -> int:

    """
    Return TRUE unread count (no limit).
    Supports optional time window.
    """

    query = "is:unread"

    if days:
        query += f" newer_than:{days}d"

    service = get_gmail_service()

    total = 0
    next_page_token = None

    while True:
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                pageToken=next_page_token,
            )
            .execute()
        )

        messages = response.get("messages", [])
        total += len(messages)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return total



def get_important_emails(limit: int = 10) -> List[Dict[str, str]]:
    service = get_gmail_service()

    response = (
        service.users()
        .messages()
        .list(userId="me", q="is:important", maxResults=limit)
        # .list(
        #     userId="me",
        #     q="in:inbox is:important -in:sent -from:me",
        #     maxResults=limit
        # )
        .execute()
    )

    messages = response.get("messages", [])
    if not messages:
        return []

    structured_emails = []

    for msg in messages:
        full_msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )

        headers = full_msg.get("payload", {}).get("headers", [])
        subject = ""
        sender = ""

        for h in headers:
            if h["name"].lower() == "subject":
                subject = h["value"].lower()
            if h["name"].lower() == "from":
                sender = h["value"].lower()

        # Filter system emails (UNCHANGED)
        system_keywords = [
            "delivery status notification",
            "mail delivery failed",
            "undeliverable",
            "failure notice",
            "postmaster",
            "mailer-daemon",
            "no-reply",
            "noreply",
        ]

        if any(k in subject for k in system_keywords):
            continue

        if any(k in sender for k in system_keywords):
            continue

        structured_emails.append(_structure_email(full_msg))

    return structured_emails
