"""Desktop orb window for Project M (Tkinter V1)."""

from __future__ import annotations

import tkinter as tk
from threading import Thread
from typing import Any

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.confirmation_manager import ConfirmationManager
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from .command_panel import CommandPanel
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
        confirmation_manager: ConfirmationManager,
        permission_manager: PermissionManager,
        sandbox: SandboxRunner,
        stt: SpeechToText | None = None,
        tts: TextToSpeech | None = None,
        voice_enabled: bool = True,
    ) -> None:
        self.interpreter = interpreter
        self.router = router
        self.memory = memory
        self.confirmation_manager = confirmation_manager
        self.permission_manager = permission_manager
        self.sandbox = sandbox
        self.stt = stt
        self.tts = tts
        self.voice_enabled = voice_enabled

        self.root = tk.Tk()
        self.root.title("Project M")
        self.root.configure(bg="#090b10")
        self.root.resizable(False, False)

        self._center_window(500, 500)

        self.canvas = tk.Canvas(self.root, width=500, height=320, bg="#090b10", highlightthickness=0)
        self.canvas.pack(pady=(10, 0))
        self.orb = OrbRenderer(self.canvas)

        self.status = StatusIndicator(self.root)
        self.status.label.pack(pady=(6, 18))

        self.panel = CommandPanel(self.root, self.handle_command, self.handle_voice_input)
        self.panel.frame.pack(pady=(0, 24))

        self.panel.focus()
        self._set_state("idle", f"Project M ready ({self.interpreter.mode} mode).")

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
        self._set_state("listening", "Listening for voice input...")
        self.root.update_idletasks()
        Thread(target=self._run_voice_capture, daemon=True).start()

    def _run_voice_capture(self) -> None:
        result = self.stt.transcribe_from_microphone()
        status = result.get("status")
        if status != "success":
            message = str(result.get("message", "Voice transcription failed."))
            self.root.after(0, lambda: self._set_state("idle", f"[WARN] {message}"))
            return

        text = str(result.get("text", "")).strip()
        if not text:
            self.root.after(0, lambda: self._set_state("idle", "[WARN] No speech detected."))
            return

        self.root.after(0, lambda: self._set_state("thinking", f'Heard: "{text}"'))
        self._run_command_in_background(text)

    def _run_command_in_background(self, text: str) -> None:
        command = self.interpreter.interpret(text)
        tool_name = command.get("tool", "unknown")

        if self.confirmation_manager.requires_confirmation(str(tool_name)):
            self.confirmation_manager.queue(command)
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
            return
        self._set_state("executing", f"Executing {command.get('tool', 'action')}...")
        Thread(target=self._run_confirmed_command, args=(command,), daemon=True).start()

    def _deny_pending_action(self) -> None:
        command = self.confirmation_manager.deny()
        if command is None:
            self._set_state("idle", "[WARN] No pending action to deny.")
            return
        tool_name = str(command.get("tool", "unknown"))
        self._set_state("idle", f"[WARN] Pending action '{tool_name}' cancelled.")

    def _run_confirmed_command(self, command: dict[str, Any]) -> None:
        result = self.sandbox.run(lambda: self.router.route(command))
        self.root.after(0, lambda: self._finalize_command(command, result))

    def _finalize_command(self, command: dict[str, Any], result: dict[str, Any]) -> None:
        self.memory.add_entry(command, result)

        status = result.get("status", "error")
        message = format_status_message(result)
        prefix = "[OK]" if status == "success" else "[WARN]"

        self._set_state("idle", f"{prefix} {message}")
        if self.tts is not None and self.voice_enabled:
            Thread(target=self.tts.speak, args=(message,), daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()
