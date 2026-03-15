"""Goal session tracking for intent-driven Project M flows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .memory_engine import MemoryEngine


class GoalSessionManager:
    """Stores and summarizes an active user goal with lightweight progress stats."""

    STATE_KEY = "active_goal_session"

    def __init__(self, memory: MemoryEngine) -> None:
        self.memory = memory

    def set_goal(self, goal_text: str) -> dict[str, Any]:
        goal = " ".join(str(goal_text).split()).strip()
        if not goal:
            return {"status": "error", "message": "Goal text is empty. Use: goal <text>."}

        session = {
            "goal": goal,
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "start_entry_id": self.memory.get_last_entry_id(),
        }
        self.memory.set_state(self.STATE_KEY, session)
        return {"status": "success", "message": f"Active goal set: {goal}", "goal": goal}

    def clear_goal(self) -> dict[str, Any]:
        session = self.get_session()
        if session is None:
            return {"status": "warning", "message": "No active goal to clear."}
        goal = str(session.get("goal", ""))
        self.memory.delete_state(self.STATE_KEY)
        return {"status": "success", "message": f"Cleared goal: {goal}"}

    def get_session(self) -> dict[str, Any] | None:
        state = self.memory.get_state(self.STATE_KEY)
        if not isinstance(state, dict):
            return None
        goal = str(state.get("goal", "")).strip()
        if not goal:
            return None
        return state

    def get_active_goal(self) -> str | None:
        session = self.get_session()
        if session is None:
            return None
        return str(session.get("goal", "")).strip() or None

    def status_report(self) -> dict[str, Any]:
        session = self.get_session()
        if session is None:
            return {
                "status": "warning",
                "message": "No active goal. Use: goal <text>.",
                "goal": None,
                "tasks_total": 0,
                "tasks_success": 0,
                "tasks_warning": 0,
                "tasks_error": 0,
                "recent": [],
            }

        start_entry_id = int(session.get("start_entry_id", 0))
        entries = self.memory.get_entries_since(start_entry_id, limit=500)
        tasks_total = len(entries)
        tasks_success = 0
        tasks_warning = 0
        tasks_error = 0
        for entry in entries:
            status = str(entry.get("result", {}).get("status", "error"))
            if status == "success":
                tasks_success += 1
            elif status == "warning":
                tasks_warning += 1
            else:
                tasks_error += 1

        recent: list[str] = []
        for entry in entries[-3:]:
            raw = str(entry.get("command", {}).get("raw_command", "")).strip()
            if raw:
                recent.append(raw)

        goal = str(session.get("goal", "")).strip()
        message = (
            f"Goal: {goal} | tasks: {tasks_total} | "
            f"success: {tasks_success}, warning: {tasks_warning}, error: {tasks_error}"
        )
        return {
            "status": "success",
            "message": message,
            "goal": goal,
            "started_at": str(session.get("started_at", "")),
            "tasks_total": tasks_total,
            "tasks_success": tasks_success,
            "tasks_warning": tasks_warning,
            "tasks_error": tasks_error,
            "recent": recent,
        }
