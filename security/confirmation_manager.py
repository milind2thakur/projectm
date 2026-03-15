"""Pending action confirmation workflow for sensitive tool execution."""

from __future__ import annotations

from typing import Any


class ConfirmationManager:
    """Tracks pending actions and enforces confirmation policy."""

    def __init__(self, required_tools: list[str] | None = None, enabled: bool = True) -> None:
        self.enabled = enabled
        self.required_tools = set(required_tools or [])
        self._pending_command: dict[str, Any] | None = None

    def requires_confirmation(self, tool_name: str) -> bool:
        if not self.enabled:
            return False
        return tool_name in self.required_tools

    def queue(self, command: dict[str, Any]) -> None:
        self._pending_command = command

    def has_pending(self) -> bool:
        return self._pending_command is not None

    def peek_pending(self) -> dict[str, Any] | None:
        return self._pending_command

    def confirm(self) -> dict[str, Any] | None:
        command = self._pending_command
        self._pending_command = None
        return command

    def deny(self) -> dict[str, Any] | None:
        command = self._pending_command
        self._pending_command = None
        return command
