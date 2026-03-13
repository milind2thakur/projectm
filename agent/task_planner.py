"""Task planner for converting interpreted commands into executable steps."""

from __future__ import annotations

from typing import Any


class TaskPlanner:
    """Builds task plans from interpreted command dictionaries.

    V1 supports single-step execution plans, while keeping a multi-step shape.
    """

    def build_plan(self, interpreted_command: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        step = {
            "tool": interpreted_command.get("tool", "unknown"),
            "args": interpreted_command.get("args", {}),
        }
        return {"steps": [step]}
