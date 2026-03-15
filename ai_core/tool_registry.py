"""Tool registry and metadata for Project M actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from tools.file_search import search_files
from tools.install_package import prepare_install
from tools.open_app import open_app
from tools.open_folder import open_folder
from tools.system_info import cpu_usage, memory_usage, storage_usage
from tools.window_control import close_window, focus_window, list_windows, minimize_window
from .workflow_templates import WorkflowTemplateEngine


@dataclass(frozen=True)
class ToolSpec:
    """Describes an executable tool and its policy metadata."""

    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    description: str
    required_permission: str = "read"
    requires_confirmation: bool = False


class ToolRegistry:
    """Registry for tool lookup, execution, and policy metadata."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        spec = self._tools.get(tool_name)
        if spec is None:
            return {
                "status": "error",
                "tool": str(tool_name),
                "message": f"Unknown tool '{tool_name}'.",
            }
        return spec.handler(args)

    def list_tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def tools_requiring_confirmation(self) -> list[str]:
        return [name for name, spec in self._tools.items() if spec.requires_confirmation]

    def tool_permissions(self) -> dict[str, str]:
        return {name: spec.required_permission for name, spec in self._tools.items()}


def build_default_registry(
    allowed_apps: list[str] | None = None,
    search_root: str | None = None,
    workflow_engine: WorkflowTemplateEngine | None = None,
) -> ToolRegistry:
    """Builds the default registry used by Project M runtime."""

    registry = ToolRegistry()
    root = Path(search_root).expanduser() if search_root else None
    workflows = workflow_engine or WorkflowTemplateEngine()

    def _run_open_app(args: dict[str, Any]) -> dict[str, Any]:
        return open_app(str(args.get("app", "")), allowed_apps=allowed_apps)

    def _run_open_folder(args: dict[str, Any]) -> dict[str, Any]:
        return open_folder(str(args.get("folder", "")))

    def _run_system_info(args: dict[str, Any]) -> dict[str, Any]:
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

    def _run_install_package(args: dict[str, Any]) -> dict[str, Any]:
        return prepare_install(str(args.get("package", "")))

    def _run_file_search(args: dict[str, Any]) -> dict[str, Any]:
        return search_files(str(args.get("query", "")), root=root)

    def _run_list_windows(_args: dict[str, Any]) -> dict[str, Any]:
        return list_windows()

    def _run_focus_window(args: dict[str, Any]) -> dict[str, Any]:
        return focus_window(str(args.get("target", "")))

    def _run_minimize_window(args: dict[str, Any]) -> dict[str, Any]:
        return minimize_window(str(args.get("target", "")))

    def _run_close_window(args: dict[str, Any]) -> dict[str, Any]:
        return close_window(str(args.get("target", "")))

    def _run_workflow_list(_args: dict[str, Any]) -> dict[str, Any]:
        items = workflows.list_workflows()
        return {
            "status": "success",
            "tool": "workflow_list",
            "message": f"Found {len(items)} workflow template(s).",
            "data": {"workflows": items},
        }

    def _run_workflow_run(args: dict[str, Any]) -> dict[str, Any]:
        requested = str(args.get("template", "")).strip()
        template = workflows.get_template(requested)
        if template is None:
            return {
                "status": "error",
                "tool": "workflow_run",
                "message": f"Unknown workflow '{requested}'.",
            }
        return {
            "status": "warning",
            "tool": "workflow_run",
            "message": f"Workflow '{template.name}' is ready to run.",
            "data": {"template": template.name, "description": template.description},
        }

    registry.register(
        ToolSpec(
            name="open_app",
            description="Open an allowlisted desktop application.",
            required_permission="read",
            handler=_run_open_app,
        )
    )
    registry.register(
        ToolSpec(
            name="open_folder",
            description="Open an allowlisted user folder.",
            required_permission="read",
            handler=_run_open_folder,
        )
    )
    registry.register(
        ToolSpec(
            name="system_info",
            description="Read system health metrics.",
            required_permission="read",
            handler=_run_system_info,
        )
    )
    registry.register(
        ToolSpec(
            name="install_package",
            description="Preview package install command.",
            required_permission="read",
            requires_confirmation=True,
            handler=_run_install_package,
        )
    )
    registry.register(
        ToolSpec(
            name="file_search",
            description="Search files by filename under configured root.",
            required_permission="read",
            handler=_run_file_search,
        )
    )
    registry.register(
        ToolSpec(
            name="list_windows",
            description="List currently open windows.",
            required_permission="read",
            handler=_run_list_windows,
        )
    )
    registry.register(
        ToolSpec(
            name="focus_window",
            description="Focus a window by title query.",
            required_permission="read",
            handler=_run_focus_window,
        )
    )
    registry.register(
        ToolSpec(
            name="minimize_window",
            description="Minimize a window by title query.",
            required_permission="read",
            handler=_run_minimize_window,
        )
    )
    registry.register(
        ToolSpec(
            name="close_window",
            description="Close a window by title query.",
            required_permission="read",
            requires_confirmation=True,
            handler=_run_close_window,
        )
    )
    registry.register(
        ToolSpec(
            name="workflow_list",
            description="List available workflow templates.",
            required_permission="read",
            handler=_run_workflow_list,
        )
    )
    registry.register(
        ToolSpec(
            name="workflow_run",
            description="Run a named multi-step workflow template.",
            required_permission="read",
            handler=_run_workflow_run,
        )
    )
    return registry
