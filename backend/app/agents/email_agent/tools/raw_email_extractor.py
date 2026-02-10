# backend/app/agents/email_agent/tools/raw_email_extractor.py

import base64
from typing import List, Dict, Any


def _decode_base64(data: str) -> str:
    """
    Decode base64url encoded string safely.
    """
    try:
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode(
            "utf-8", errors="ignore"
        )
    except Exception:
        return ""


def _extract_body(payload: Dict[str, Any]) -> str:
    """
    Recursively extract email body text from Gmail message payload.
    """
    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")

    # Plain text or HTML body
    if data:
        return _decode_base64(data)

    # Multipart message: recurse through parts
    parts = payload.get("parts", [])
    for part in parts:
        text = _extract_body(part)
        if text:
            return text

    return ""


def _extract_headers(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Convert Gmail headers list into a dictionary.
    """
    result = {}
    for header in headers:
        name = header.get("name")
        value = header.get("value")
        if name and value:
            result[name.lower()] = value
    return result


def extract_email_text(messages: List[Dict[str, Any]]) -> List[str]:
    """
    Normalize raw Gmail messages into clean text strings.

    Output format per email:
    - Subject
    - From
    - Date
    - Body (decoded)

    Returns:
    - List[str]
    """

    extracted_emails: List[str] = []

    for msg in messages:
        payload = msg.get("payload", {})
        headers = _extract_headers(payload.get("headers", []))

        subject = headers.get("subject", "(no subject)")
        sender = headers.get("from", "(unknown sender)")
        date = headers.get("date", "(unknown date)")

        body_text = _extract_body(payload).strip()

        email_text = (
            f"Subject: {subject}\n"
            f"From: {sender}\n"
            f"Date: {date}\n\n"
            f"{body_text}"
        )

        extracted_emails.append(email_text)

    return extracted_emails
