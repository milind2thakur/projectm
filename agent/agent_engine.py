"""Main Agent Engine orchestration controller."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner

from .agent_state import AgentState
from .execution_manager import ExecutionManager
from .task_planner import TaskPlanner

StateCallback = Callable[[str], None]


class AgentEngine:
    """Coordinates interpret -> plan -> execute for user requests."""

    def __init__(
        self,
        interpreter: CommandInterpreter,
        router: ToolRouter,
        memory: MemoryEngine,
        permission_manager: PermissionManager,
        sandbox: SandboxRunner,
    ) -> None:
        self.interpreter = interpreter
        self.router = router
        self.memory = memory
        self.state = AgentState()
        self.task_planner = TaskPlanner()
        self.execution_manager = ExecutionManager(router, permission_manager, sandbox)

    def _set_state(self, state: str, callback: StateCallback | None = None) -> None:
        self.state.set_state(state)
        if callback is not None:
            callback(state)

    def handle_user_input(self, user_command: str, on_state_change: StateCallback | None = None) -> dict[str, Any]:
        self._set_state(AgentState.LISTENING, on_state_change)

        interpreted = self.interpreter.interpret(user_command)

        self._set_state(AgentState.THINKING, on_state_change)
        plan = self.task_planner.build_plan(interpreted)

        self._set_state(AgentState.EXECUTING, on_state_change)
        execution_result = self.execution_manager.run_plan(plan)

        self.memory.add_entry(interpreted, execution_result)

        if execution_result.get("status") != "success":
            self._set_state(AgentState.ERROR, on_state_change)
            response = {
                "status": "error",
                "command": user_command,
                "message": execution_result.get("message", "Execution failed."),
                "failed_step": execution_result.get("failed_step"),
                "steps_executed": execution_result.get("steps_executed", []),
            }
            self._set_state(AgentState.IDLE, on_state_change)
            return response

        response = {
            "status": "success",
            "command": user_command,
            "steps_executed": execution_result.get("steps_executed", []),
            "result": execution_result.get("result", {}),
        }
        self._set_state(AgentState.IDLE, on_state_change)
        return response
