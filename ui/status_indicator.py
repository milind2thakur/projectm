"""Status label helper for OrbWindow."""

from __future__ import annotations

import tkinter as tk


class StatusIndicator:
    """Manages user-facing status text updates."""

    def __init__(self, parent: tk.Widget) -> None:
        self.var = tk.StringVar(value="How can I help you?")
        self.label = tk.Label(
            parent,
            textvariable=self.var,
            bg="#090b10",
            fg="#9ca3af",
            font=("Arial", 11),
            wraplength=420,
            justify=tk.CENTER,
        )

    def set(self, text: str) -> None:
        self.var.set(text)
