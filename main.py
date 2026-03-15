"""Project M desktop entrypoint."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from typing import Any

import yaml

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from ui.result_formatter import format_status_message
from ui.orb_window import OrbWindow


def load_settings(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def run_terminal_mode(
    interpreter: CommandInterpreter,
    router: ToolRouter,
    memory: MemoryEngine,
    permission_manager: PermissionManager,
    sandbox: SandboxRunner,
) -> None:
    print("Project M terminal mode is active.")
    print("Type a command, or 'exit' to quit.")
    while True:
        try:
            user_text = input("projectm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Project M.")
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"}:
            print("Exiting Project M.")
            break

        command = interpreter.interpret(user_text)
        tool_name = str(command.get("tool", "unknown"))
        if not permission_manager.can_execute(tool_name, granted_level="read"):
            result: dict[str, Any] = {
                "status": "error",
                "tool": tool_name,
                "message": "Permission denied for current granted level.",
            }
        else:
            result = sandbox.run(lambda: router.route(command))

        memory.add_entry(command, result)
        prefix = "[OK]" if result.get("status") == "success" else "[WARN]"
        print(f"{prefix} {format_status_message(result)}")


def main() -> None:
    settings = load_settings(Path("config/settings.yaml"))

    interpreter = CommandInterpreter(
        model_path="models/projectm.gguf" if settings.get("mode") != "fallback" else None
    )
    router = ToolRouter(
        allowed_apps=settings.get("allowed_apps"),
        search_root=settings.get("default_search_root"),
    )
    memory = MemoryEngine()
    permission_manager = PermissionManager()
    sandbox = SandboxRunner()

    try:
        app = OrbWindow(
            interpreter=interpreter,
            router=router,
            memory=memory,
            permission_manager=permission_manager,
            sandbox=sandbox,
        )
        app.run()
    except tk.TclError as exc:
        print("Project M GUI could not start (Tk/Tcl not configured).")
        print("Falling back to terminal mode.")
        print(f"Technical details: {exc}")
        run_terminal_mode(interpreter, router, memory, permission_manager, sandbox)


if __name__ == "__main__":
    main()
