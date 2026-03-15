"""Adaptive planner for converting active goals into executable plan steps."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .memory_engine import MemoryEngine


class AdaptivePlanner:
    """Builds and tracks a lightweight executable plan for an active goal."""

    STATE_KEY = "active_goal_plan"

    def __init__(self, memory: MemoryEngine) -> None:
        self.memory = memory

    def has_active_plan(self) -> bool:
        return self.get_plan() is not None

    def get_plan(self) -> dict[str, Any] | None:
        state = self.memory.get_state(self.STATE_KEY)
        if not isinstance(state, dict):
            return None
        steps = state.get("steps")
        if not isinstance(steps, list):
            return None
        goal = str(state.get("goal", "")).strip()
        if not goal:
            return None
        return state

    def clear_plan(self) -> dict[str, Any]:
        plan = self.get_plan()
        if plan is None:
            return {"status": "warning", "message": "No active plan to clear."}
        goal = str(plan.get("goal", "")).strip()
        self.memory.delete_state(self.STATE_KEY)
        return {"status": "success", "message": f"Cleared plan for goal: {goal}"}

    def generate_plan(self, goal_text: str) -> dict[str, Any]:
        goal = " ".join(str(goal_text).split()).strip()
        if not goal:
            return {"status": "error", "message": "Cannot generate plan: goal is empty."}

        steps = self._build_steps(goal)
        plan = {
            "goal": goal,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "next_step_index": 0,
            "steps": steps,
        }
        self.memory.set_state(self.STATE_KEY, plan)
        return {
            "status": "success",
            "message": f"Generated plan with {len(steps)} step(s) for goal: {goal}",
            "data": {
                "goal": goal,
                "total_steps": len(steps),
                "next_commands": [str(step.get("raw_command", "")) for step in steps[:3]],
            },
        }

    def set_next_step_index(self, next_step_index: int) -> None:
        plan = self.get_plan()
        if plan is None:
            return
        total = len(plan.get("steps", []))
        clamped = min(max(0, int(next_step_index)), total)
        plan["next_step_index"] = clamped
        plan["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.memory.set_state(self.STATE_KEY, plan)

    def status_report(self) -> dict[str, Any]:
        plan = self.get_plan()
        if plan is None:
            return {
                "status": "warning",
                "message": "No active plan. Use: plan goal",
                "goal": None,
                "total_steps": 0,
                "completed_steps": 0,
                "remaining_steps": 0,
                "next_step_index": 0,
                "next_commands": [],
            }

        steps = plan.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        total_steps = len(steps)
        next_step_index = min(max(0, int(plan.get("next_step_index", 0))), total_steps)
        completed_steps = next_step_index
        remaining_steps = total_steps - completed_steps
        next_commands: list[str] = []
        for step in steps[next_step_index : next_step_index + 3]:
            command_text = str(step.get("raw_command", "")).strip()
            if command_text:
                next_commands.append(command_text)

        goal = str(plan.get("goal", "")).strip()
        message = (
            f"Plan for goal '{goal}': {completed_steps}/{total_steps} step(s) completed, "
            f"{remaining_steps} remaining."
        )
        return {
            "status": "success",
            "message": message,
            "goal": goal,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "remaining_steps": remaining_steps,
            "next_step_index": next_step_index,
            "next_commands": next_commands,
        }

    def _build_steps(self, goal_text: str) -> list[dict[str, Any]]:
        goal = goal_text.lower()
        steps: list[dict[str, Any]] = []

        if any(token in goal for token in ("code", "coding", "build", "prototype", "dev", "debug")):
            steps.extend(
                [
                    {"tool": "open_folder", "args": {"folder": "Documents"}, "raw_command": "open documents"},
                    {"tool": "open_app", "args": {"app": "code"}, "raw_command": "open code"},
                    {"tool": "open_app", "args": {"app": "x-terminal-emulator"}, "raw_command": "open terminal"},
                    {"tool": "list_windows", "args": {}, "raw_command": "list windows"},
                ]
            )
        elif any(token in goal for token in ("health", "performance", "cpu", "memory", "disk", "storage")):
            steps.extend(
                [
                    {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
                    {"tool": "system_info", "args": {"metric": "memory"}, "raw_command": "show memory usage"},
                    {"tool": "system_info", "args": {"metric": "storage"}, "raw_command": "show storage usage"},
                    {"tool": "list_windows", "args": {}, "raw_command": "list windows"},
                ]
            )
        elif any(token in goal for token in ("research", "learn", "study", "read", "browser")):
            steps.extend(
                [
                    {"tool": "open_app", "args": {"app": "firefox"}, "raw_command": "open firefox"},
                    {"tool": "open_folder", "args": {"folder": "Downloads"}, "raw_command": "open downloads"},
                    {"tool": "list_windows", "args": {}, "raw_command": "list windows"},
                ]
            )
        else:
            steps.extend(
                [
                    {"tool": "workflow_list", "args": {}, "raw_command": "list workflows"},
                    {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
                    {"tool": "list_windows", "args": {}, "raw_command": "list windows"},
                ]
            )

        app_candidates = ["firefox", "code", "vlc", "discord", "telegram-desktop", "spotify"]
        for app in app_candidates:
            if app in goal:
                steps.insert(
                    0,
                    {"tool": "open_app", "args": {"app": app}, "raw_command": f"open {app}"},
                )

        folder_candidates = {"downloads": "Downloads", "documents": "Documents", "desktop": "Desktop"}
        for token, folder_name in folder_candidates.items():
            if token in goal:
                steps.insert(
                    0,
                    {"tool": "open_folder", "args": {"folder": folder_name}, "raw_command": f"open {token}"},
                )

        unique_steps: list[dict[str, Any]] = []
        seen: set[str] = set()
        for step in steps:
            signature = f"{step.get('tool', '')}:{json.dumps(step.get('args', {}), sort_keys=True)}"
            if signature in seen:
                continue
            seen.add(signature)
            unique_steps.append(step)
        return unique_steps
