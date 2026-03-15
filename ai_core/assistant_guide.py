"""Context-aware next-step suggestions for Project M."""

from __future__ import annotations

from typing import Any

from .memory_engine import MemoryEngine


class AssistantGuide:
    """Produces lightweight, context-aware suggestions for the next action."""

    def _goal_actions(self, active_goal: str, has_active_plan: bool = False) -> list[str]:
        goal = active_goal.lower()
        if has_active_plan:
            actions = ["plan run", "plan show", "goal status"]
        else:
            actions = ["plan goal", "goal status"]
        if any(token in goal for token in ("code", "coding", "build", "project", "dev")):
            actions.append("open coding workspace")
        elif any(token in goal for token in ("health", "performance", "cpu", "memory", "disk")):
            actions.append("summarize system health")
        elif any(token in goal for token in ("window", "desktop", "app")):
            actions.append("list windows")
        else:
            actions.append("list workflows")
        actions.append("goal clear")
        return actions

    def suggest_next(
        self,
        memory: MemoryEngine,
        pending_command: dict[str, Any] | None = None,
        active_goal: str | None = None,
        has_active_plan: bool = False,
        limit: int = 3,
    ) -> list[str]:
        if limit <= 0:
            return []

        suggestions: list[str] = []
        if isinstance(pending_command, dict):
            tool_name = str(pending_command.get("tool", "action"))
            suggestions.extend(
                [
                    "confirm",
                    "deny",
                    f"Pending: {tool_name}",
                ]
            )
            return suggestions[:limit]

        if active_goal:
            suggestions.extend(self._goal_actions(active_goal, has_active_plan=has_active_plan))

        last_entry = memory.get_last_entry()
        if last_entry is None:
            suggestions.extend(["open coding workspace", "show cpu usage", "list workflows"])
            return suggestions[:limit]

        command = last_entry.get("command", {})
        result = last_entry.get("result", {})
        tool_name = str(command.get("tool", "unknown"))
        status = str(result.get("status", "unknown"))

        if status != "success":
            suggestions.extend(["resume", "show cpu usage", "list workflows"])
        elif tool_name == "system_info":
            suggestions.extend(["summarize system health", "list windows", "open terminal"])
        elif tool_name == "open_app":
            app_name = str(command.get("args", {}).get("app", "")).strip()
            if app_name:
                suggestions.append(f"focus {app_name}")
            suggestions.extend(["list windows", "show cpu usage"])
        elif tool_name == "open_folder":
            suggestions.extend(["find <keyword>", "open terminal", "list windows"])
        elif tool_name == "file_search":
            suggestions.extend(["open downloads", "open documents", "resume"])
        elif tool_name == "workflow_run":
            suggestions.extend(["resume", "show cpu usage", "list windows"])
        elif tool_name in {"list_windows", "focus_window", "minimize_window", "close_window"}:
            suggestions.extend(["list windows", "focus <title>", "open coding workspace"])
        else:
            suggestions.extend(["show cpu usage", "list workflows", "open coding workspace"])

        # Keep ordering stable while removing duplicates/empty items.
        unique: list[str] = []
        seen: set[str] = set()
        for item in suggestions:
            normalized = item.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique.append(item)

        return unique[:limit]
