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


def print_terminal_help() -> None:
    print("Available commands:")
    print("  help                 Show this help text")
    print("  history [n]          Show the most recent n commands (default: 5)")
    print("  exit | quit          Exit Project M")
    print("  open firefox         Open an allowed app")
    print("  open downloads       Open an allowed folder")
    print("  show cpu usage       Show CPU usage")
    print("  show memory usage    Show memory usage")
    print("  show storage usage   Show storage usage")
    print("  find <query>         Search file names under configured root")
    print("  install <package>    Show install preview command")


def print_terminal_history(memory: MemoryEngine, limit: int = 5) -> None:
    history = memory.get_history(limit=limit)
    if not history:
        print("No command history yet.")
        return
    for index, entry in enumerate(history, start=1):
        command = entry.get("command", {})
        raw = command.get("raw_command", "<unknown>")
        result = entry.get("result", {})
        status = result.get("status", "unknown")
        print(f"{index}. {raw} -> {status}")


def run_terminal_mode(
    interpreter: CommandInterpreter,
    router: ToolRouter,
    memory: MemoryEngine,
    permission_manager: PermissionManager,
    sandbox: SandboxRunner,
) -> None:
    print("Project M terminal mode is active.")
    print("Type a command, 'help' for options, or 'exit' to quit.")
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

        if user_text.lower() in {"help", "?"}:
            print_terminal_help()
            continue

        if user_text.lower().startswith("history"):
            parts = user_text.split()
            limit = 5
            if len(parts) > 1 and parts[1].isdigit():
                limit = max(1, int(parts[1]))
            print_terminal_history(memory, limit=limit)
            continue

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
