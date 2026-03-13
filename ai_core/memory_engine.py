"""Lightweight in-memory memory engine."""

from __future__ import annotations

from typing import Any


class MemoryEngine:
    """Stores command history and quick access to recent entries."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._last_successful_tool_call: dict[str, Any] | None = None

    def add_entry(self, command: dict[str, Any], result: dict[str, Any]) -> None:
        entry = {"command": command, "result": result}
        self._history.append(entry)
        if result.get("status") == "success":
            self._last_successful_tool_call = entry

    def get_last_entry(self) -> dict[str, Any] | None:
        if not self._history:
            return None
        return self._history[-1]

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        return self._history[-limit:]
