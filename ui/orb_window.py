"""Desktop orb window for Project M (Tkinter V1)."""

from __future__ import annotations

import tkinter as tk
from threading import Thread
from typing import Any

from ai_core.assistant_guide import AssistantGuide
from ai_core.command_interpreter import CommandInterpreter
from ai_core.goal_session import GoalSessionManager
from ai_core.memory_engine import MemoryEngine
from ai_core.telemetry_logger import TelemetryLogger
from ai_core.tool_router import ToolRouter
from ai_core.workflow_runner import run_workflow_template
from ai_core.workflow_templates import WorkflowTemplateEngine
from security.confirmation_manager import ConfirmationManager
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from .command_panel import CommandPanel
from .context_panel import ContextPanel
from .orb_renderer import OrbRenderer
from .result_formatter import format_status_message
from .status_indicator import StatusIndicator


class OrbWindow:
    """Main desktop window that wires UI interactions to backend modules."""

    def __init__(
        self,
        interpreter: CommandInterpreter,
        router: ToolRouter,
        memory: MemoryEngine,
        workflow_engine: WorkflowTemplateEngine,
        confirmation_manager: ConfirmationManager,
        permission_manager: PermissionManager,
        sandbox: SandboxRunner,
        assistant_guide: AssistantGuide,
        goal_session: GoalSessionManager,
        telemetry: TelemetryLogger | None = None,
        stt: SpeechToText | None = None,
        tts: TextToSpeech | None = None,
        voice_enabled: bool = True,
        voice_capture_seconds: int = 4,
        voice_capture_retries: int = 1,
        voice_push_to_talk_key: str = "F8",
    ) -> None:
        self.interpreter = interpreter
        self.router = router
        self.memory = memory
        self.workflow_engine = workflow_engine
        self.confirmation_manager = confirmation_manager
        self.permission_manager = permission_manager
        self.sandbox = sandbox
        self.assistant_guide = assistant_guide
        self.goal_session = goal_session
        self.telemetry = telemetry
        self.stt = stt
        self.tts = tts
        self.voice_enabled = voice_enabled
        self.voice_capture_seconds = max(1, voice_capture_seconds)
        self.voice_capture_retries = max(1, voice_capture_retries)
        self.voice_push_to_talk_key = voice_push_to_talk_key
        self._voice_capture_active = False

        self.root = tk.Tk()
        self.root.title("Project M")
        self.root.configure(bg="#090b10")
        self.root.resizable(False, False)

        self._center_window(500, 500)

        self.canvas = tk.Canvas(self.root, width=500, height=320, bg="#090b10", highlightthickness=0)
        self.canvas.pack(pady=(10, 0))
        self.orb = OrbRenderer(self.canvas)

        self.status = StatusIndicator(self.root)
        self.status.label.pack(pady=(6, 8))

        self.context = ContextPanel(self.root)
        self.context.frame.pack(pady=(0, 10))

        self.panel = CommandPanel(self.root, self.handle_command, self.handle_voice_input)
        self.panel.frame.pack(pady=(0, 24))

        self.panel.focus()
        self._set_state("idle", f"Project M ready ({self.interpreter.mode} mode).")
        self._bind_push_to_talk_key()
        self._refresh_context_panel()
        if self.telemetry is not None:
            self.telemetry.log_event("gui_mode_started", {"interpreter_mode": self.interpreter.mode})

    def _center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = int((screen_w - width) / 2)
        y = int((screen_h - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _set_state(self, state: str, message: str) -> None:
        self.orb.set_state(state)
        self.status.set(message)

    def handle_command(self, text: str) -> None:
        normalized = text.strip().lower()
        if self.telemetry is not None:
            self.telemetry.log_event("user_input", {"source": "gui", "text": text})

        if normalized in {"quit", "exit"}:
            self._set_state("idle", "Shutting down Project M...")
            self.root.after(150, self.root.destroy)
            return

        if normalized in {"confirm", "yes"}:
            self._confirm_pending_action()
            return

        if normalized in {"deny", "cancel", "no"}:
            self._deny_pending_action()
            return

        if normalized in {"resume", "resume last task"}:
            self._resume_last_task()
            return

        if normalized == "goal":
            self._show_goal_status()
            return

        if normalized == "goal status":
            self._show_goal_status()
            return

        if normalized == "goal clear":
            self._clear_goal()
            return

        if normalized.startswith("goal "):
            self._set_goal(text[5:].strip())
            return

        self._set_state("thinking", "Thinking...")
        self.root.update_idletasks()
        Thread(target=self._run_command_in_background, args=(text,), daemon=True).start()

    def handle_voice_input(self) -> None:
        if not self.voice_enabled:
            self._set_state("idle", "[WARN] Voice input is disabled in settings.")
            return
        if self.stt is None:
            self._set_state("idle", "[WARN] Speech-to-text module not available.")
            return
        if self._voice_capture_active:
            self._set_state("idle", "[WARN] Voice capture is already in progress.")
            return

        self._voice_capture_active = True
        if self.telemetry is not None:
            self.telemetry.log_event(
                "voice_capture_started",
                {
                    "source": "gui",
                    "seconds": self.voice_capture_seconds,
                    "retries": self.voice_capture_retries,
                },
            )
        self._set_state(
            "listening",
            f"Listening for voice input ({self.voice_capture_seconds}s, up to {self.voice_capture_retries} attempt(s))...",
        )
        self.root.update_idletasks()
        Thread(target=self._run_voice_capture, daemon=True).start()

    def _run_voice_capture(self) -> None:
        try:
            result = self.stt.transcribe_from_microphone(
                seconds=self.voice_capture_seconds,
                retries=self.voice_capture_retries,
            )
            status = result.get("status")
            if status != "success":
                message = str(result.get("message", "Voice transcription failed."))
                if self.telemetry is not None:
                    self.telemetry.log_event(
                        "voice_capture_failed",
                        {
                            "source": "gui",
                            "status": str(result.get("status", "error")),
                            "message": message,
                        },
                    )
                self.root.after(0, lambda: self._set_state("idle", f"[WARN] {message}"))
                return

            text = str(result.get("text", "")).strip()
            if not text:
                self.root.after(0, lambda: self._set_state("idle", "[WARN] No speech detected."))
                return

            if self.telemetry is not None:
                self.telemetry.log_event("voice_capture_success", {"source": "gui", "text": text})
            self.root.after(0, lambda: self._set_state("thinking", f'Heard: "{text}"'))
            self._run_command_in_background(text)
        finally:
            self._voice_capture_active = False

    def _run_command_in_background(self, text: str) -> None:
        command = self.interpreter.interpret(text)
        tool_name = command.get("tool", "unknown")

        if tool_name == "workflow_list":
            result = self.router.route(command)
            self.root.after(0, lambda: self._finalize_command(command, result))
            return

        if tool_name == "workflow_run":
            template_name = str(command.get("args", {}).get("template", ""))
            result = run_workflow_template(template_name, self.workflow_engine, self._execute_workflow_step)
            self.root.after(0, lambda: self._finalize_command(command, result))
            return

        if self.confirmation_manager.requires_confirmation(str(tool_name)):
            self.confirmation_manager.queue(command)
            if self.telemetry is not None:
                self.telemetry.log_event(
                    "confirmation_queued",
                    {"source": "gui", "tool": str(tool_name)},
                )
            result = {
                "status": "warning",
                "tool": str(tool_name),
                "message": "Confirmation required. Type 'confirm' to proceed or 'deny' to cancel.",
            }
            self.root.after(0, lambda: self._finalize_command(command, result))
            return

        if not self.permission_manager.can_execute(tool_name, granted_level="read"):
            result = {
                "status": "error",
                "tool": tool_name,
                "message": "Permission denied for current granted level.",
            }
        else:
            self.root.after(0, lambda: self._set_state("executing", f"Executing {tool_name}..."))
            result = self.sandbox.run(lambda: self.router.route(command))

        self.root.after(0, lambda: self._finalize_command(command, result))

    def _confirm_pending_action(self) -> None:
        command = self.confirmation_manager.confirm()
        if command is None:
            self._set_state("idle", "[WARN] No pending action to confirm.")
            self._refresh_context_panel()
            return
        if self.telemetry is not None:
            self.telemetry.log_event(
                "confirmation_confirmed",
                {"source": "gui", "tool": str(command.get("tool", "unknown"))},
            )
        self._set_state("executing", f"Executing {command.get('tool', 'action')}...")
        self._refresh_context_panel()
        Thread(target=self._run_confirmed_command, args=(command,), daemon=True).start()

    def _deny_pending_action(self) -> None:
        command = self.confirmation_manager.deny()
        if command is None:
            self._set_state("idle", "[WARN] No pending action to deny.")
            self._refresh_context_panel()
            return
        tool_name = str(command.get("tool", "unknown"))
        if self.telemetry is not None:
            self.telemetry.log_event(
                "confirmation_denied",
                {"source": "gui", "tool": tool_name},
            )
        self._set_state("idle", f"[WARN] Pending action '{tool_name}' cancelled.")
        self._refresh_context_panel()

    def _resume_last_task(self) -> None:
        last_entry = self.memory.get_last_entry()
        if last_entry is None:
            self._set_state("idle", "[WARN] No previous task to resume.")
            self._refresh_context_panel()
            return
        command = last_entry.get("command")
        if not isinstance(command, dict):
            self._set_state("idle", "[WARN] Last task data is invalid.")
            self._refresh_context_panel()
            return
        tool_name = str(command.get("tool", "unknown"))
        if self.confirmation_manager.requires_confirmation(tool_name):
            self.confirmation_manager.queue(command)
            self._set_state("idle", "[WARN] Confirmation required to resume. Type 'confirm' or 'deny'.")
            self._refresh_context_panel()
            return
        self._set_state("executing", f"Resuming {tool_name}...")
        Thread(target=self._run_confirmed_command, args=(command,), daemon=True).start()

    def _run_confirmed_command(self, command: dict[str, Any]) -> None:
        tool_name = str(command.get("tool", "unknown"))
        if tool_name == "workflow_run":
            template_name = str(command.get("args", {}).get("template", ""))
            result = run_workflow_template(template_name, self.workflow_engine, self._execute_workflow_step)
        else:
            result = self.sandbox.run(lambda: self.router.route(command))
        self.root.after(0, lambda: self._finalize_command(command, result))

    def _show_goal_status(self) -> None:
        status = self.goal_session.status_report()
        if status.get("status") != "success":
            self._set_state("idle", f"[WARN] {status.get('message', 'No active goal.')}")
        else:
            self._set_state("idle", f"[OK] {status.get('message', '')}")
        if self.telemetry is not None:
            self.telemetry.log_event(
                "goal_status_requested",
                {
                    "source": "gui",
                    "has_goal": bool(status.get("goal")),
                    "tasks_total": int(status.get("tasks_total", 0)),
                },
            )
        self._refresh_context_panel()

    def _set_goal(self, goal_text: str) -> None:
        result = self.goal_session.set_goal(goal_text)
        prefix = "[OK]" if result.get("status") == "success" else "[WARN]"
        self._set_state("idle", f"{prefix} {result.get('message', '')}")
        if self.telemetry is not None:
            self.telemetry.log_event(
                "goal_set",
                {
                    "source": "gui",
                    "status": str(result.get("status", "unknown")),
                    "goal": str(result.get("goal", "")),
                },
            )
        self._refresh_context_panel()

    def _clear_goal(self) -> None:
        result = self.goal_session.clear_goal()
        prefix = "[OK]" if result.get("status") == "success" else "[WARN]"
        self._set_state("idle", f"{prefix} {result.get('message', '')}")
        if self.telemetry is not None:
            self.telemetry.log_event(
                "goal_cleared",
                {"source": "gui", "status": str(result.get("status", "unknown"))},
            )
        self._refresh_context_panel()

    def _execute_workflow_step(self, step_command: dict[str, Any]) -> dict[str, Any]:
        tool_name = str(step_command.get("tool", "unknown"))
        if self.confirmation_manager.requires_confirmation(tool_name):
            return {
                "status": "warning",
                "tool": tool_name,
                "message": "Skipped confirmation-required step during workflow run.",
            }
        if not self.permission_manager.can_execute(tool_name, granted_level="read"):
            return {
                "status": "error",
                "tool": tool_name,
                "message": "Permission denied for current granted level.",
            }
        result = self.sandbox.run(lambda: self.router.route(step_command))
        self.memory.add_entry(step_command, result)
        return result

    def _finalize_command(self, command: dict[str, Any], result: dict[str, Any]) -> None:
        self.memory.add_entry(command, result)
        if self.telemetry is not None:
            self.telemetry.log_event(
                "command_result",
                {
                    "source": "gui",
                    "tool": str(command.get("tool", "unknown")),
                    "status": str(result.get("status", "error")),
                    "message": str(result.get("message", "")),
                },
            )

        status = result.get("status", "error")
        message = format_status_message(result)
        prefix = "[OK]" if status == "success" else "[WARN]"

        self._set_state("idle", f"{prefix} {message}")
        self._refresh_context_panel()
        if self.tts is not None and self.voice_enabled:
            Thread(target=self.tts.speak, args=(message,), daemon=True).start()

    def _bind_push_to_talk_key(self) -> None:
        if not self.voice_enabled:
            return
        key_name = str(self.voice_push_to_talk_key).strip()
        if not key_name:
            return
        self.root.bind(f"<{key_name}>", self._on_push_to_talk_key)

    def _on_push_to_talk_key(self, _event: tk.Event) -> None:
        if self.telemetry is not None:
            self.telemetry.log_event("push_to_talk_triggered", {"key": self.voice_push_to_talk_key})
        self.handle_voice_input()

    def _refresh_context_panel(self) -> None:
        history = self.memory.get_history(limit=3)
        last_command = "-"
        last_status = "-"
        recent: list[str] = []

        for entry in history:
            command = entry.get("command", {})
            recent.append(str(command.get("raw_command", "<unknown>")))

        if history:
            last = history[-1]
            last_command = str(last.get("command", {}).get("raw_command", "-"))
            last_status = str(last.get("result", {}).get("status", "-"))

        pending = self.confirmation_manager.peek_pending()
        pending_label = str(pending.get("tool", "none")) if isinstance(pending, dict) else "none"
        pending_command = pending if isinstance(pending, dict) else None
        active_goal = self.goal_session.get_active_goal()
        suggestions = self.assistant_guide.suggest_next(
            memory=self.memory,
            pending_command=pending_command,
            active_goal=active_goal,
            limit=3,
        )
        goal_label = active_goal or "none"
        self.context.set(
            last_command=last_command,
            last_status=last_status,
            goal=goal_label,
            pending=pending_label,
            recent=recent,
            suggestions=suggestions,
        )

    def run(self) -> None:
        self.root.mainloop()
