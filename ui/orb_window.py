"""Desktop orb window for Project M (Tkinter V1)."""

from __future__ import annotations

import tkinter as tk

from agent.agent_engine import AgentEngine
from agent.agent_state import AgentState
from .command_panel import CommandPanel
from .orb_renderer import OrbRenderer
from .status_indicator import StatusIndicator


STATE_TO_ORB = {
    AgentState.IDLE: "idle",
    AgentState.LISTENING: "listening",
    AgentState.THINKING: "thinking",
    AgentState.EXECUTING: "executing",
    AgentState.ERROR: "thinking",
}


class OrbWindow:
    """Main desktop window that wires UI interactions to AgentEngine."""

    def __init__(self, agent_engine: AgentEngine) -> None:
        self.agent_engine = agent_engine

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
        self._update_ui_state("Project M ready.")

    def _center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = int((screen_w - width) / 2)
        y = int((screen_h - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _update_ui_state(self, message: str) -> None:
        current = self.agent_engine.state.get_state()
        orb_state = STATE_TO_ORB.get(current, "idle")
        self.orb.set_state(orb_state)
        self.status.set(message)
        self.root.update_idletasks()

    def _sync_state(self, _state: str) -> None:
        self._update_ui_state(self.status.var.get())

    def handle_command(self, text: str) -> None:
        normalized = text.strip().lower()

        if normalized in {"quit", "exit"}:
            self.agent_engine.state.set_state(AgentState.IDLE)
            self._update_ui_state("Shutting down Project M...")
            self.root.after(150, self.root.destroy)
            return

        if normalized == "[voice placeholder]":
            self.agent_engine.state.set_state(AgentState.LISTENING)
            self._update_ui_state("Voice input is a placeholder in V1.")
            self.root.after(900, lambda: self._after_command_message("How can I help you?"))
            return

        self._update_ui_state("Processing request...")
        result = self.agent_engine.handle_user_input(text, on_state_change=self._sync_state)

        status = result.get("status", "error")
        prefix = "✅" if status == "success" else "⚠️"

        if status == "success":
            final = result.get("result", {})
            message = final.get("message", "Done.") if isinstance(final, dict) else "Done."
        else:
            message = str(result.get("message", "Execution failed."))

        self._after_command_message(f"{prefix} {message}")

    def _after_command_message(self, message: str) -> None:
        self.agent_engine.state.set_state(AgentState.IDLE)
        self._update_ui_state(message)

    def run(self) -> None:
        self.root.mainloop()
