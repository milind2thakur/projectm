"""Sandbox execution concept for running tool actions safely."""

from __future__ import annotations

from collections.abc import Callable

from permission_manager import PermissionManager


class SandboxRunner:
    """Prototype sandbox runner that gates execution with permissions."""

    def __init__(self, permission_manager: PermissionManager | None = None) -> None:
        self.permission_manager = permission_manager or PermissionManager()

    def execute(self, action: str, callback: Callable[[], str]) -> str:
        if not self.permission_manager.is_allowed(action):
            return f"Permission denied for action: {action}"
        return callback()
