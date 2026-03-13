"""Terminal-based orb status renderer."""

from __future__ import annotations


class OrbInterface:
    def show_idle(self) -> None:
        print("[◉] Project M is idle")

    def show_listening(self) -> None:
        print("[◎] Listening...")

    def show_thinking(self) -> None:
        print("[◌] Thinking...")

    def show_executing(self) -> None:
        print("[●] Executing tool...")
