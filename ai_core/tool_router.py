"""Tool routing layer for Project M."""

from __future__ import annotations

from typing import Any

from .tool_registry import ToolRegistry, build_default_registry
from .workflow_templates import WorkflowTemplateEngine


class ToolRouter:
    """Routes structured commands to concrete tool functions."""

    def __init__(
        self,
        allowed_apps: list[str] | None = None,
        search_root: str | None = None,
        workflow_engine: WorkflowTemplateEngine | None = None,
        registry: ToolRegistry | None = None,
    ) -> None:
        self._registry = registry or build_default_registry(
            allowed_apps=allowed_apps,
            search_root=search_root,
            workflow_engine=workflow_engine,
        )

    def route(self, command: dict[str, Any]) -> dict[str, Any]:
        tool_name = str(command.get("tool", "unknown"))
        args = command.get("args", {})
        if not isinstance(args, dict):
            args = {}
        return self._registry.execute(tool_name, args)

    def list_tools(self) -> list[str]:
        return self._registry.list_tool_names()

    def tools_requiring_confirmation(self) -> list[str]:
        return self._registry.tools_requiring_confirmation()

    def tool_permissions(self) -> dict[str, str]:
        return self._registry.tool_permissions()
