"""Main Agent Engine orchestration controller."""

from __future__ import annotations

from typing import Any

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner

from .agent_state import AgentState
from .execution_manager import ExecutionManager
from .task_planner import TaskPlanner


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

    def handle_user_input(self, user_command: str) -> dict[str, Any]:
        # 1) User command received.
        self.state.set_state(AgentState.LISTENING)

        # 2) Interpret command into structured tool intent.
        interpreted = self.interpreter.interpret(user_command)

        # 3) Plan step(s) to execute.
        self.state.set_state(AgentState.THINKING)
        plan = self.task_planner.build_plan(interpreted)

        # 4) Execute planned steps.
        self.state.set_state(AgentState.EXECUTING)
        execution_result = self.execution_manager.run_plan(plan)

        # 5) Persist run in memory and finalize state.
        self.memory.add_entry(interpreted, execution_result)

        if execution_result.get("status") != "success":
            self.state.set_state(AgentState.ERROR)
            return {
                "status": "error",
                "command": user_command,
                "message": execution_result.get("message", "Execution failed."),
                "failed_step": execution_result.get("failed_step"),
                "steps_executed": execution_result.get("steps_executed", []),
            }

        self.state.set_state(AgentState.IDLE)
        return {
            "status": "success",
            "command": user_command,
            "steps_executed": execution_result.get("steps_executed", []),
            "result": execution_result.get("result", {}),
        }
