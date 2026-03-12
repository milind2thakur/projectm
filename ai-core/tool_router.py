"""Maps structured tool calls to concrete system tools."""

from __future__ import annotations

from typing import Any, Callable

from tools.file_search import run as file_search
from tools.install_package import run as install_package
from tools.open_app import run as open_app
from tools.open_folder import run as open_folder
from tools.system_info import run as system_info


class ToolRouter:
    """Selects and executes tools based on structured tool calls."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[[str], str]] = {
            "open_folder": open_folder,
            "open_app": open_app,
            "file_search": file_search,
            "system_info": system_info,
            "install_package": install_package,
        }

    def route_and_execute(self, tool_call: dict[str, Any]) -> str:
        tool = str(tool_call.get("tool", "")).strip().lower()

        if tool == "open_folder":
            path = str(tool_call.get("path", "")).strip()
            return self._tools[tool](path)

        if tool == "open_app":
            app_name = str(tool_call.get("app_name", "")).strip()
            return self._tools[tool](app_name)

        if tool == "file_search":
            query = str(tool_call.get("query", "")).strip()
            return self._tools[tool](query)

        if tool == "system_info":
            return self._tools[tool]("")

        if tool == "install_package":
            package = str(tool_call.get("package", "")).strip()
            return self._tools[tool](package)

        return f"No tool matched for tool call: {tool_call}"
