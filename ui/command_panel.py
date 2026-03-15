"""Command input panel for OrbWindow."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class CommandPanel:
    """Encapsulates text input and submit behavior."""

    def __init__(
        self,
        parent: tk.Widget,
        on_submit: Callable[[str], None],
        on_voice: Callable[[], None] | None = None,
    ) -> None:
        self._on_submit = on_submit
        self._on_voice = on_voice
        self.frame = tk.Frame(parent, bg="#090b10")

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            self.frame,
            textvariable=self.input_var,
            bg="#111827",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            relief=tk.FLAT,
            font=("Arial", 12),
            width=30,
        )
        self.entry.bind("<Return>", self._handle_submit)
        self.entry.pack(side=tk.LEFT, padx=(0, 8), ipady=8)

        self.mic_button = tk.Button(
            self.frame,
            text="Mic",
            bg="#1f2937",
            fg="#e5e7eb",
            relief=tk.FLAT,
            width=4,
            command=self._mic_action,
        )
        self.mic_button.pack(side=tk.LEFT)

    def _handle_submit(self, _event: tk.Event) -> None:
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._on_submit(text)

    def _mic_action(self) -> None:
        if self._on_voice is not None:
            self._on_voice()
            return
        self._on_submit("[voice placeholder]")

    def focus(self) -> None:
        self.entry.focus_set()
