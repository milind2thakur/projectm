"""Workflow templates for multi-step task orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowTemplate:
    name: str
    description: str
    steps: list[dict[str, Any]]


class WorkflowTemplateEngine:
    """Holds predefined workflow templates and alias resolution."""

    def __init__(self) -> None:
        self._templates: dict[str, WorkflowTemplate] = {
            "coding_workspace": WorkflowTemplate(
                name="coding_workspace",
                description="Open a coding setup (folder + editor + terminal).",
                steps=[
                    {"tool": "open_folder", "args": {"folder": "Documents"}, "raw_command": "open documents"},
                    {"tool": "open_app", "args": {"app": "code"}, "raw_command": "open code"},
                    {
                        "tool": "open_app",
                        "args": {"app": "x-terminal-emulator"},
                        "raw_command": "open terminal",
                    },
                ],
            ),
            "system_health": WorkflowTemplate(
                name="system_health",
                description="Collect CPU, memory, and storage usage.",
                steps=[
                    {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
                    {"tool": "system_info", "args": {"metric": "memory"}, "raw_command": "show memory usage"},
                    {"tool": "system_info", "args": {"metric": "storage"}, "raw_command": "show storage usage"},
                ],
            ),
            "research_session": WorkflowTemplate(
                name="research_session",
                description="Open browser and downloads workspace.",
                steps=[
                    {"tool": "open_app", "args": {"app": "firefox"}, "raw_command": "open firefox"},
                    {"tool": "open_folder", "args": {"folder": "Downloads"}, "raw_command": "open downloads"},
                ],
            ),
        }

        self._aliases = {
            "coding": "coding_workspace",
            "coding_workspace": "coding_workspace",
            "open coding workspace": "coding_workspace",
            "start coding workflow": "coding_workspace",
            "system_health": "system_health",
            "system health": "system_health",
            "summarize system health": "system_health",
            "research": "research_session",
            "research_session": "research_session",
            "research session": "research_session",
        }

    def list_workflows(self) -> list[dict[str, str]]:
        return [
            {"name": template.name, "description": template.description}
            for template in self._templates.values()
        ]

    def resolve_name(self, value: str) -> str | None:
        key = value.strip().lower()
        if key in self._templates:
            return key
        return self._aliases.get(key)

    def get_template(self, value: str) -> WorkflowTemplate | None:
        name = self.resolve_name(value)
        if name is None:
            return None
        return self._templates.get(name)
