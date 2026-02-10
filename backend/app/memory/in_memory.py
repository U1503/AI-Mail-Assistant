from langchain_core.chat_history import InMemoryChatMessageHistory
from typing import Dict


class MemoryStore:
    """
    Simple in-memory store for chat histories.
    Keyed by session_id.
    """

    def __init__(self):
        self._store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_history(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self._store:
            self._store[session_id] = InMemoryChatMessageHistory()
        return self._store[session_id]


# Singleton
memory_store = MemoryStore()
