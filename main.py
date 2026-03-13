"""Project M desktop entrypoint."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from ui.orb_window import OrbWindow


def load_settings(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def main() -> None:
    settings = load_settings(Path("config/settings.yaml"))

    interpreter = CommandInterpreter(
        model_path="models/projectm.gguf" if settings.get("mode") != "fallback" else None
    )
    router = ToolRouter()
    memory = MemoryEngine()
    permission_manager = PermissionManager()
    sandbox = SandboxRunner()

    app = OrbWindow(
        interpreter=interpreter,
        router=router,
        memory=memory,
        permission_manager=permission_manager,
        sandbox=sandbox,
    )
    app.run()


if __name__ == "__main__":
    main()
