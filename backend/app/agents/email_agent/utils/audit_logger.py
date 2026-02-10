
# NOTE: Not used. Will be replaced by DB-backed audit logging later.



from datetime import datetime
from typing import List, Dict

# In-memory audit log (can be DB later)
EMAIL_AUDIT_LOG: List[Dict] = []


def log_email_sent(to: str, subject: str):
    EMAIL_AUDIT_LOG.append({
        "timestamp": datetime.utcnow().isoformat(),
        "to": to,
        "subject": subject,
        "status": "sent"
    })


def get_email_audit_log() -> List[Dict]:
    return EMAIL_AUDIT_LOG
