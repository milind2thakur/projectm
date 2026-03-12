"""In-memory short-term memory for recent interactions."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List


class MemoryEngine:
    """Stores recent command/response pairs for context."""

    def __init__(self, max_items: int = 20) -> None:
        self._history: Deque[Dict[str, str]] = deque(maxlen=max_items)

    def add(self, user_command: str, interpretation: str) -> None:
        self._history.append(
            {
                "user_command": user_command,
                "interpretation": interpretation,
            }
        )

    def recent(self) -> List[Dict[str, str]]:
        return list(self._history)
