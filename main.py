"""Project M desktop/CLI entrypoint."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from agent.agent_engine import AgentEngine
from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from ui.orb_window import OrbWindow


def load_settings(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def should_launch_gui() -> bool:
    """Return True when a desktop display server appears available."""
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def build_agent_engine(settings: dict) -> AgentEngine:
    interpreter = CommandInterpreter(
        model_path="models/projectm.gguf" if settings.get("mode") != "fallback" else None
    )
    router = ToolRouter()
    memory = MemoryEngine()
    permission_manager = PermissionManager()
    sandbox = SandboxRunner()
    return AgentEngine(
        interpreter=interpreter,
        router=router,
        memory=memory,
        permission_manager=permission_manager,
        sandbox=sandbox,
    )


def run_cli(agent_engine: AgentEngine) -> None:
    """Headless-safe fallback loop when no GUI display is available."""
    print("Project M (CLI fallback) started. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("\nYou> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye from Project M.")
            return
        result = agent_engine.handle_user_input(user_input)
        print(result)


def main() -> None:
    settings = load_settings(Path("config/settings.yaml"))
    agent_engine = build_agent_engine(settings)

    if should_launch_gui():
        app = OrbWindow(agent_engine=agent_engine)
        app.run()
    else:
        run_cli(agent_engine)


if __name__ == "__main__":
    main()
