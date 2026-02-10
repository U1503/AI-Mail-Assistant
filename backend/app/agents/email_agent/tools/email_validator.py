import re
import dns.resolver
from typing import List


# RFC 5322 simplified regex (safe & practical)
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def is_valid_email_format(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def has_mx_record(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception:
        return False


def validate_emails(
    emails: List[str],
    check_mx: bool = False
) -> List[str]:
    """
    Returns list of valid emails
    """

    valid_emails = []

    for email in emails:
        if not is_valid_email_format(email):
            continue

        if check_mx:
            domain = email.split("@")[1]
            if not has_mx_record(domain):
                continue

        valid_emails.append(email)

    return valid_emails
