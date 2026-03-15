"""Context panel for recent actions and pending confirmations."""

from __future__ import annotations

import tkinter as tk


class ContextPanel:
    """Displays lightweight runtime context in the main UI."""

    def __init__(self, parent: tk.Widget) -> None:
        self.frame = tk.Frame(parent, bg="#090b10")
        self.var = tk.StringVar(value="Last: -\nStatus: -\nGoal: none\nPending: none\nRecent: -\nNext: -")
        self.label = tk.Label(
            self.frame,
            textvariable=self.var,
            bg="#090b10",
            fg="#6b7280",
            font=("Arial", 10),
            justify=tk.LEFT,
            anchor="w",
            width=58,
        )
        self.label.pack()

    def set(
        self,
        last_command: str,
        last_status: str,
        goal: str,
        pending: str,
        recent: list[str],
        suggestions: list[str],
    ) -> None:
        recent_text = ", ".join(recent[-3:]) if recent else "-"
        suggestions_text = ", ".join(suggestions[:3]) if suggestions else "-"
        self.var.set(
            f"Last: {last_command or '-'}\n"
            f"Status: {last_status or '-'}\n"
            f"Goal: {goal or 'none'}\n"
            f"Pending: {pending or 'none'}\n"
            f"Recent: {recent_text}\n"
            f"Next: {suggestions_text}"
        )
