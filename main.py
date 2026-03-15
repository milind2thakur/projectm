"""Project M desktop entrypoint."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from typing import Any

import yaml

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from security.confirmation_manager import ConfirmationManager
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from ui.result_formatter import format_status_message
from ui.orb_window import OrbWindow
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech


def load_settings(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def print_terminal_help() -> None:
    print("Available commands:")
    print("  help                 Show this help text")
    print("  history [n]          Show the most recent n commands (default: 5)")
    print("  voice                Capture voice command from microphone")
    print("  confirm              Approve pending sensitive action")
    print("  deny                 Reject pending sensitive action")
    print("  exit | quit          Exit Project M")
    print("  open firefox         Open an allowed app")
    print("  open downloads       Open an allowed folder")
    print("  show cpu usage       Show CPU usage")
    print("  show memory usage    Show memory usage")
    print("  show storage usage   Show storage usage")
    print("  find <query>         Search file names under configured root")
    print("  install <package>    Show install preview command")
    print("  list windows         List open windows")
    print("  focus <title>        Focus window by title")
    print("  minimize <title>     Minimize window by title")
    print("  close <title>        Close window by title (requires confirmation)")


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
    confirmation_manager: ConfirmationManager,
    permission_manager: PermissionManager,
    sandbox: SandboxRunner,
    stt: SpeechToText | None = None,
    tts: TextToSpeech | None = None,
    voice_enabled: bool = True,
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

        if user_text.lower() in {"confirm", "yes"}:
            command = confirmation_manager.confirm()
            if command is None:
                print("[WARN] No pending action to confirm.")
                continue
            result = sandbox.run(lambda: router.route(command))
            memory.add_entry(command, result)
            prefix = "[OK]" if result.get("status") == "success" else "[WARN]"
            spoken_text = format_status_message(result)
            print(f"{prefix} {spoken_text}")
            if voice_enabled and tts is not None:
                tts.speak(spoken_text)
            continue

        if user_text.lower() in {"deny", "cancel", "no"}:
            command = confirmation_manager.deny()
            if command is None:
                print("[WARN] No pending action to deny.")
                continue
            print(f"[WARN] Pending action '{command.get('tool', 'unknown')}' cancelled.")
            continue

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

        if user_text.lower() == "voice":
            if not voice_enabled:
                print("[WARN] Voice input is disabled in settings.")
                continue
            if stt is None:
                print("[WARN] Speech-to-text module not available.")
                continue
            print("Listening...")
            stt_result = stt.transcribe_from_microphone()
            if stt_result.get("status") != "success":
                print(f"[WARN] {stt_result.get('message', 'Voice transcription failed.')}")
                continue
            user_text = str(stt_result.get("text", "")).strip()
            if not user_text:
                print("[WARN] No speech detected.")
                continue
            print(f'Heard: "{user_text}"')

        command = interpreter.interpret(user_text)
        tool_name = str(command.get("tool", "unknown"))
        if confirmation_manager.requires_confirmation(tool_name):
            confirmation_manager.queue(command)
            print("[WARN] Confirmation required. Type 'confirm' to proceed or 'deny' to cancel.")
            continue

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
        spoken_text = format_status_message(result)
        print(f"{prefix} {spoken_text}")
        if voice_enabled and tts is not None:
            tts.speak(spoken_text)


def main() -> None:
    settings = load_settings(Path("config/settings.yaml"))

    router = ToolRouter(
        allowed_apps=settings.get("allowed_apps"),
        search_root=settings.get("default_search_root"),
    )
    interpreter = CommandInterpreter(
        model_path="models/projectm.gguf" if settings.get("mode") != "fallback" else None
    )
    interpreter.allowed_tools = router.list_tools()
    memory = MemoryEngine(db_path=str(settings.get("memory_db_path", "data/projectm_memory.db")))
    confirmation_tools = settings.get("confirmation_required_tools")
    if confirmation_tools is None:
        confirmation_tools = router.tools_requiring_confirmation()
    confirmation_manager = ConfirmationManager(
        required_tools=list(confirmation_tools),
        enabled=bool(settings.get("confirmation_enabled", True)),
    )
    permission_manager = PermissionManager(tool_permissions=router.tool_permissions())
    sandbox = SandboxRunner()
    voice_enabled = bool(settings.get("voice_enabled", True))
    stt = SpeechToText(model_name=str(settings.get("stt_model", "base")))
    tts = TextToSpeech()

    try:
        app = OrbWindow(
            interpreter=interpreter,
            router=router,
            memory=memory,
            confirmation_manager=confirmation_manager,
            permission_manager=permission_manager,
            sandbox=sandbox,
            stt=stt,
            tts=tts,
            voice_enabled=voice_enabled,
        )
        app.run()
    except tk.TclError as exc:
        print("Project M GUI could not start (Tk/Tcl not configured).")
        print("Falling back to terminal mode.")
        print(f"Technical details: {exc}")
        run_terminal_mode(
            interpreter,
            router,
            memory,
            confirmation_manager,
            permission_manager,
            sandbox,
            stt=stt,
            tts=tts,
            voice_enabled=voice_enabled,
        )


if __name__ == "__main__":
    main()
