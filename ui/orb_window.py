"""Desktop orb window for Project M (Tkinter V1)."""

from __future__ import annotations

import tkinter as tk

from ai_core.command_interpreter import CommandInterpreter
from ai_core.memory_engine import MemoryEngine
from ai_core.tool_router import ToolRouter
from security.permission_manager import PermissionManager
from security.sandbox_runner import SandboxRunner
from .command_panel import CommandPanel
from .orb_renderer import OrbRenderer
from .status_indicator import StatusIndicator


class OrbWindow:
    """Main desktop window that wires UI interactions to backend modules."""

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
        self.permission_manager = permission_manager
        self.sandbox = sandbox

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

        self.panel = CommandPanel(self.root, self.handle_command)
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

        if normalized == "[voice placeholder]":
            self._set_state("listening", "Voice input is a placeholder in V1.")
            self.root.after(900, lambda: self._set_state("idle", "How can I help you?"))
            return

        self._set_state("thinking", "Thinking...")
        self.root.update_idletasks()

        command = self.interpreter.interpret(text)
        tool_name = command.get("tool", "unknown")

        if not self.permission_manager.can_execute(tool_name, granted_level="read"):
            result = {
                "status": "error",
                "tool": tool_name,
                "message": "Permission denied for current granted level.",
            }
        else:
            self._set_state("executing", f"Executing {tool_name}...")
            self.root.update_idletasks()
            result = self.sandbox.run(lambda: self.router.route(command))

        self.memory.add_entry(command, result)

        status = result.get("status", "error")
        message = result.get("message", "No message")
        prefix = "✅" if status == "success" else "⚠️"

        data = result.get("data")
        if isinstance(data, dict) and "command_preview" in data:
            message = f"{message} ({data['command_preview']})"

        self._set_state("idle", f"{prefix} {message}")

    def run(self) -> None:
        self.root.mainloop()
