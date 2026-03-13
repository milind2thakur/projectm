"""Execution manager for running planned task steps safely."""

from __future__ import annotations

from typing import Any

from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner


class ExecutionManager:
    """Executes task steps sequentially and handles partial failures."""

    def __init__(
        self,
        router: ToolRouter,
        permission_manager: PermissionManager,
        sandbox: SandboxRunner,
        granted_level: str = "read",
    ) -> None:
        self.router = router
        self.permission_manager = permission_manager
        self.sandbox = sandbox
        self.granted_level = granted_level

    def run_plan(self, plan: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
        steps = plan.get("steps", [])
        executed: list[dict[str, Any]] = []

        for step in steps:
            tool_name = str(step.get("tool", "unknown"))
            if not self.permission_manager.can_execute(tool_name, granted_level=self.granted_level):
                return {
                    "status": "error",
                    "message": "Permission denied for current granted level.",
                    "failed_step": step,
                    "steps_executed": executed,
                }

            command = {"tool": tool_name, "args": step.get("args", {})}
            try:
                result = self.sandbox.run(lambda cmd=command: self.router.route(cmd))
            except Exception as exc:  # pragma: no cover - defensive UI safety net
                result = {
                    "status": "error",
                    "tool": tool_name,
                    "message": f"Tool execution failed: {exc}",
                }

            record = {"step": step, "result": result}
            executed.append(record)

            if result.get("status") != "success":
                return {
                    "status": "error",
                    "message": result.get("message", "Step execution failed."),
                    "failed_step": step,
                    "steps_executed": executed,
                }

        return {
            "status": "success",
            "steps_executed": executed,
            "result": executed[-1]["result"] if executed else {},
        }
