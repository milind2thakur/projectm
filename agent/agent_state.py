"""Runtime state tracking for Agent Engine."""

from __future__ import annotations


class AgentState:
    """Tracks high-level agent execution state."""

    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"

    def __init__(self) -> None:
        self._state = self.IDLE

    def set_state(self, state: str) -> None:
        self._state = state

    def get_state(self) -> str:
        return self._state
