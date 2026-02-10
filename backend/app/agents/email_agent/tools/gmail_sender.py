# backend/app/agents/email_agent/tools/gmail_sender.py

import base64
from email.message import EmailMessage
from typing import Dict, List, Union

from app.agents.email_agent.tools.gmail_utils import get_gmail_service


def _build_message(
    to: Union[str, List[str]],
    subject: str,
    body: str,
    cc: List[str] | None = None,
    bcc: List[str] | None = None,
) -> dict:
    """
    Build a Gmail API compatible message.
    """

    message = EmailMessage()
    message.set_content(body)

    message["To"] = ", ".join(to) if isinstance(to, list) else to
    message["Subject"] = subject

    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    return {"raw": encoded_message}


def send_email(payload: Dict) -> Dict:
    """
    Send an email using Gmail API.

    Expected payload:
    {
        "to": "abc@gmail.com" | ["a@gmail.com", "b@gmail.com"],
        "subject": "Subject text",
        "body": "Email body",
        "cc": [...],        # optional
        "bcc": [...],       # optional
    }
    """

    if not payload:
        raise ValueError("Email payload is required")

    to = payload.get("to")
    subject = payload.get("subject")
    body = payload.get("body")

    if not to or not subject or not body:
        raise ValueError("Email must include 'to', 'subject', and 'body'")

    service = get_gmail_service()

    message = _build_message(
        to=to,
        subject=subject,
        body=body,
        cc=payload.get("cc"),
        bcc=payload.get("bcc"),
    )

    result = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )

    return {
        "status": "sent",
        "message_id": result.get("id"),
    }
