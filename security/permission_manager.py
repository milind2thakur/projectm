"""Permission level checks for tool execution."""

from __future__ import annotations


class PermissionManager:
    """Basic permission gating for tool execution.

    V1 defaults to `read`. Preview-only install commands are also `read`.
    """

    LEVEL_ORDER = {"read": 1, "write": 2, "admin": 3}
    DEFAULT_TOOL_PERMISSIONS = {
        "open_app": "read",
        "open_folder": "read",
        "file_search": "read",
        "system_info": "read",
        "install_package": "read",
        "unknown": "read",
    }

    def __init__(self, tool_permissions: dict[str, str] | None = None) -> None:
        self.tool_permissions = dict(self.DEFAULT_TOOL_PERMISSIONS)
        if tool_permissions:
            self.tool_permissions.update(tool_permissions)

    def can_execute(self, tool_name: str, granted_level: str = "read") -> bool:
        required = self.tool_permissions.get(tool_name, "admin")
        granted_rank = self.LEVEL_ORDER.get(granted_level, 1)
        required_rank = self.LEVEL_ORDER.get(required, 3)
        return granted_rank >= required_rank
