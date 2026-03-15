"""Project M desktop entrypoint."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from typing import Any

import yaml

from ai_core.assistant_guide import AssistantGuide
from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.telemetry_logger import TelemetryLogger
from ai_core.workflow_runner import run_workflow_template
from ai_core.workflow_templates import WorkflowTemplateEngine
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
    print("  ptt                  Alias for voice capture")
    print("  confirm              Approve pending sensitive action")
    print("  deny                 Reject pending sensitive action")
    print("  resume               Re-run the most recent task")
    print("  next                 Show suggested next actions")
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
    print("  list workflows       List workflow templates")
    print("  run workflow <name>  Run a workflow template")


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


def print_terminal_suggestions(
    assistant_guide: AssistantGuide,
    memory: MemoryEngine,
    confirmation_manager: ConfirmationManager,
    limit: int = 3,
) -> list[str]:
    pending = confirmation_manager.peek_pending()
    pending_command = pending if isinstance(pending, dict) else None
    suggestions = assistant_guide.suggest_next(memory, pending_command=pending_command, limit=limit)
    if suggestions:
        print(f"Next: {', '.join(suggestions)}")
    else:
        print("Next: no suggestions yet.")
    return suggestions


def run_terminal_mode(
    interpreter: CommandInterpreter,
    router: ToolRouter,
    memory: MemoryEngine,
    workflow_engine: WorkflowTemplateEngine,
    confirmation_manager: ConfirmationManager,
    permission_manager: PermissionManager,
    sandbox: SandboxRunner,
    assistant_guide: AssistantGuide,
    telemetry: TelemetryLogger | None = None,
    stt: SpeechToText | None = None,
    tts: TextToSpeech | None = None,
    voice_enabled: bool = True,
    voice_capture_seconds: int = 4,
    voice_capture_retries: int = 1,
) -> None:
    if telemetry is not None:
        telemetry.log_event("terminal_mode_started", {"interpreter_mode": interpreter.mode})

    print("Project M terminal mode is active.")
    print("Type a command, 'help' for options, or 'exit' to quit.")
    print_terminal_suggestions(assistant_guide, memory, confirmation_manager)

    def _print_result(command: dict[str, Any], result: dict[str, Any]) -> None:
        memory.add_entry(command, result)
        if telemetry is not None:
            telemetry.log_event(
                "command_result",
                {
                    "source": "terminal",
                    "tool": str(command.get("tool", "unknown")),
                    "status": str(result.get("status", "error")),
                    "message": str(result.get("message", "")),
                },
            )
        prefix = "[OK]" if result.get("status") == "success" else "[WARN]"
        spoken_text = format_status_message(result)
        print(f"{prefix} {spoken_text}")
        if voice_enabled and tts is not None:
            tts.speak(spoken_text)
        suggestions = print_terminal_suggestions(assistant_guide, memory, confirmation_manager)
        if telemetry is not None:
            telemetry.log_event(
                "assistant_suggestions_shown",
                {"source": "terminal", "suggestions": suggestions},
            )

    while True:
        try:
            user_text = input("projectm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Project M.")
            break

        if not user_text:
            continue
        if telemetry is not None:
            telemetry.log_event("user_input", {"source": "terminal", "text": user_text})

        normalized = user_text.lower()

        if normalized in {"exit", "quit"}:
            if telemetry is not None:
                telemetry.log_event("terminal_mode_exit", {"reason": "user_exit"})
            print("Exiting Project M.")
            break

        if normalized in {"confirm", "yes"}:
            command = confirmation_manager.confirm()
            if command is None:
                print("[WARN] No pending action to confirm.")
                continue
            if telemetry is not None:
                telemetry.log_event(
                    "confirmation_confirmed",
                    {"source": "terminal", "tool": str(command.get("tool", "unknown"))},
                )
            result = sandbox.run(lambda: router.route(command))
            _print_result(command, result)
            continue

        if normalized in {"deny", "cancel", "no"}:
            command = confirmation_manager.deny()
            if command is None:
                print("[WARN] No pending action to deny.")
                continue
            if telemetry is not None:
                telemetry.log_event(
                    "confirmation_denied",
                    {"source": "terminal", "tool": str(command.get("tool", "unknown"))},
                )
            print(f"[WARN] Pending action '{command.get('tool', 'unknown')}' cancelled.")
            continue

        if normalized in {"help", "?"}:
            print_terminal_help()
            continue

        if normalized in {"next", "suggest", "suggestions"}:
            suggestions = print_terminal_suggestions(assistant_guide, memory, confirmation_manager)
            if telemetry is not None:
                telemetry.log_event(
                    "assistant_suggestions_shown",
                    {"source": "terminal", "suggestions": suggestions},
                )
            continue

        if normalized in {"resume", "resume last task"}:
            last_entry = memory.get_last_entry()
            if last_entry is None:
                print("[WARN] No previous task to resume.")
                continue
            command = last_entry.get("command")
            if not isinstance(command, dict):
                print("[WARN] Last task data is invalid.")
                continue
            tool_name = str(command.get("tool", "unknown"))
            if confirmation_manager.requires_confirmation(tool_name):
                confirmation_manager.queue(command)
                print("[WARN] Confirmation required to resume. Type 'confirm' or 'deny'.")
                continue
            if tool_name == "workflow_run":
                template_name = str(command.get("args", {}).get("template", ""))

                def _resume_step(step_command: dict[str, Any]) -> dict[str, Any]:
                    step_tool = str(step_command.get("tool", "unknown"))
                    if confirmation_manager.requires_confirmation(step_tool):
                        return {
                            "status": "warning",
                            "tool": step_tool,
                            "message": "Skipped confirmation-required step during workflow run.",
                        }
                    if not permission_manager.can_execute(step_tool, granted_level="read"):
                        return {
                            "status": "error",
                            "tool": step_tool,
                            "message": "Permission denied for current granted level.",
                        }
                    step_result = sandbox.run(lambda: router.route(step_command))
                    memory.add_entry(step_command, step_result)
                    return step_result

                result = run_workflow_template(template_name, workflow_engine, _resume_step)
            else:
                result = sandbox.run(lambda: router.route(command))
            _print_result(command, result)
            continue

        if normalized.startswith("history"):
            parts = user_text.split()
            limit = 5
            if len(parts) > 1 and parts[1].isdigit():
                limit = max(1, int(parts[1]))
            print_terminal_history(memory, limit=limit)
            continue

        if normalized in {"voice", "ptt"}:
            if not voice_enabled:
                print("[WARN] Voice input is disabled in settings.")
                continue
            if stt is None:
                print("[WARN] Speech-to-text module not available.")
                continue
            print(
                f"Listening... ({max(1, voice_capture_seconds)}s, "
                f"up to {max(1, voice_capture_retries)} attempt(s))"
            )
            if telemetry is not None:
                telemetry.log_event(
                    "voice_capture_started",
                    {
                        "source": "terminal",
                        "seconds": max(1, voice_capture_seconds),
                        "retries": max(1, voice_capture_retries),
                    },
                )
            stt_result = stt.transcribe_from_microphone(
                seconds=voice_capture_seconds,
                retries=voice_capture_retries,
            )
            if stt_result.get("status") != "success":
                if telemetry is not None:
                    telemetry.log_event(
                        "voice_capture_failed",
                        {
                            "source": "terminal",
                            "status": str(stt_result.get("status", "error")),
                            "message": str(stt_result.get("message", "")),
                        },
                    )
                print(f"[WARN] {stt_result.get('message', 'Voice transcription failed.')}")
                continue
            user_text = str(stt_result.get("text", "")).strip()
            if not user_text:
                print("[WARN] No speech detected.")
                continue
            print(f'Heard: "{user_text}"')
            if telemetry is not None:
                telemetry.log_event("voice_capture_success", {"source": "terminal", "text": user_text})

        command = interpreter.interpret(user_text)
        tool_name = str(command.get("tool", "unknown"))

        if tool_name == "workflow_list":
            result = router.route(command)
            _print_result(command, result)
            continue

        if tool_name == "workflow_run":
            template_name = str(command.get("args", {}).get("template", ""))

            def _execute_step(step_command: dict[str, Any]) -> dict[str, Any]:
                step_tool = str(step_command.get("tool", "unknown"))
                if confirmation_manager.requires_confirmation(step_tool):
                    return {
                        "status": "warning",
                        "tool": step_tool,
                        "message": "Skipped confirmation-required step during workflow run.",
                    }
                if not permission_manager.can_execute(step_tool, granted_level="read"):
                    return {
                        "status": "error",
                        "tool": step_tool,
                        "message": "Permission denied for current granted level.",
                    }
                result = sandbox.run(lambda: router.route(step_command))
                memory.add_entry(step_command, result)
                return result

            workflow_result = run_workflow_template(template_name, workflow_engine, _execute_step)
            _print_result(command, workflow_result)
            continue

        if confirmation_manager.requires_confirmation(tool_name):
            confirmation_manager.queue(command)
            if telemetry is not None:
                telemetry.log_event(
                    "confirmation_queued",
                    {"source": "terminal", "tool": tool_name},
                )
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

        _print_result(command, result)


def main() -> None:
    settings = load_settings(Path("config/settings.yaml"))
    workflow_engine = WorkflowTemplateEngine()

    router = ToolRouter(
        allowed_apps=settings.get("allowed_apps"),
        search_root=settings.get("default_search_root"),
        workflow_engine=workflow_engine,
    )
    interpreter = CommandInterpreter(
        model_path="models/projectm.gguf" if settings.get("mode") != "fallback" else None
    )
    interpreter.allowed_tools = router.list_tools()
    memory = MemoryEngine(db_path=str(settings.get("memory_db_path", "data/projectm_memory.db")))
    assistant_guide = AssistantGuide()
    confirmation_tools = settings.get("confirmation_required_tools")
    if confirmation_tools is None:
        confirmation_tools = router.tools_requiring_confirmation()
    confirmation_manager = ConfirmationManager(
        required_tools=list(confirmation_tools),
        enabled=bool(settings.get("confirmation_enabled", True)),
    )
    permission_manager = PermissionManager(tool_permissions=router.tool_permissions())
    sandbox = SandboxRunner()
    telemetry = TelemetryLogger(
        enabled=bool(settings.get("telemetry_enabled", True)),
        log_path=str(settings.get("telemetry_log_path", "logs/projectm_events.jsonl")),
    )
    voice_enabled = bool(settings.get("voice_enabled", True))
    voice_capture_seconds = int(settings.get("voice_capture_seconds", 4))
    voice_capture_retries = int(settings.get("voice_capture_retries", 1))
    voice_push_to_talk_key = str(settings.get("voice_push_to_talk_key", "F8"))
    stt = SpeechToText(
        model_name=str(settings.get("stt_model", "base")),
        capture_seconds=voice_capture_seconds,
        capture_retries=voice_capture_retries,
    )
    tts = TextToSpeech()
    telemetry.log_event(
        "app_started",
        {
            "interpreter_mode": interpreter.mode,
            "voice_enabled": voice_enabled,
        },
    )

    try:
        app = OrbWindow(
            interpreter=interpreter,
            router=router,
            memory=memory,
            workflow_engine=workflow_engine,
            confirmation_manager=confirmation_manager,
            permission_manager=permission_manager,
            sandbox=sandbox,
            assistant_guide=assistant_guide,
            telemetry=telemetry,
            stt=stt,
            tts=tts,
            voice_enabled=voice_enabled,
            voice_capture_seconds=voice_capture_seconds,
            voice_capture_retries=voice_capture_retries,
            voice_push_to_talk_key=voice_push_to_talk_key,
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
            workflow_engine,
            confirmation_manager,
            permission_manager,
            sandbox,
            assistant_guide,
            telemetry=telemetry,
            stt=stt,
            tts=tts,
            voice_enabled=voice_enabled,
            voice_capture_seconds=voice_capture_seconds,
            voice_capture_retries=voice_capture_retries,
        )


if __name__ == "__main__":
    main()
