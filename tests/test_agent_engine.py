from agent.agent_engine import AgentEngine
from agent.agent_state import AgentState
from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner


def _build_engine() -> AgentEngine:
    interpreter = CommandInterpreter(model_path=None)
    router = ToolRouter()
    memory = MemoryEngine()
    permission_manager = PermissionManager()
    sandbox = SandboxRunner()
    return AgentEngine(interpreter, router, memory, permission_manager, sandbox)


def test_agent_engine_success_flow() -> None:
    engine = _build_engine()
    result = engine.handle_user_input("find invoice")
    assert result["status"] == "success"
    assert result["steps_executed"]
    assert engine.state.get_state() == AgentState.IDLE


def test_agent_engine_permission_error() -> None:
    engine = _build_engine()
    result = engine.handle_user_input("install numpy")
    assert result["status"] == "error"
    assert result["failed_step"]["tool"] == "install_package"
    assert engine.state.get_state() == AgentState.ERROR
