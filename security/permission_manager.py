"""Permission policy checks for Project M tool usage."""

from __future__ import annotations


class PermissionManager:
    """Minimal permission manager with allow-list checks."""

    def __init__(self) -> None:
        self._sensitive_prefixes = ("install package",)

    def is_allowed(self, action: str) -> bool:
        normalized = action.strip().lower()
        return not any(normalized.startswith(prefix) for prefix in self._sensitive_prefixes)
