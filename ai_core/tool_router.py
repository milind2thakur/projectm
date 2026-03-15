"""Tool routing layer for Project M."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from tools.file_search import search_files
from tools.install_package import prepare_install
from tools.open_app import open_app
from tools.open_folder import open_folder
from tools.system_info import cpu_usage, memory_usage, storage_usage


class ToolRouter:
    """Routes structured commands to concrete tool functions."""

    def __init__(self, allowed_apps: list[str] | None = None, search_root: str | None = None) -> None:
        self._allowed_apps = allowed_apps
        self._search_root = Path(search_root).expanduser() if search_root else None
        self._routes: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "open_app": self._run_open_app,
            "open_folder": self._run_open_folder,
            "system_info": self._run_system_info,
            "install_package": self._run_install_package,
            "file_search": self._run_file_search,
        }

    def route(self, command: dict[str, Any]) -> dict[str, Any]:
        tool_name = command.get("tool", "unknown")
        handler = self._routes.get(tool_name)
        if handler is None:
            return {
                "status": "error",
                "tool": str(tool_name),
                "message": f"Unknown tool '{tool_name}'.",
            }
        return handler(command.get("args", {}))

    def _run_open_app(self, args: dict[str, Any]) -> dict[str, Any]:
        return open_app(str(args.get("app", "")), allowed_apps=self._allowed_apps)

    def _run_open_folder(self, args: dict[str, Any]) -> dict[str, Any]:
        return open_folder(str(args.get("folder", "")))

    def _run_system_info(self, args: dict[str, Any]) -> dict[str, Any]:
        metric = str(args.get("metric", "")).lower()
        if metric == "cpu":
            data = cpu_usage()
        elif metric == "memory":
            data = memory_usage()
        elif metric == "storage":
            data = storage_usage()
        else:
            return {"status": "error", "tool": "system_info", "message": "Unknown system info metric."}
        return {"status": "success", "tool": "system_info", "message": f"Retrieved {metric} usage.", "data": data}

    def _run_install_package(self, args: dict[str, Any]) -> dict[str, Any]:
        return prepare_install(str(args.get("package", "")))

    def _run_file_search(self, args: dict[str, Any]) -> dict[str, Any]:
        return search_files(str(args.get("query", "")), root=self._search_root)
