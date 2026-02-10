from langchain_groq import ChatGroq
from app.core.config import get_settings

settings = get_settings()

# -------------------------------------------------
# Singleton LLM instance
# -------------------------------------------------

_llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model=settings.LLM_MODEL,
    temperature=0,
)


def get_llm():
    """
    Return the singleton LLM instance.
    """
    return _llm


def is_confirmation(user_message: str) -> bool:
    """
    Deterministic confirmation detection.
    Avoid LLM to prevent false positives.
    """
    clean = user_message.strip().lower()

    return clean in {
        "yes",
        "yes!",
        "yes please",
        "yes please!",
        "sure",
        "okay",
        "ok",
        "confirm",
        "please do",
    }

