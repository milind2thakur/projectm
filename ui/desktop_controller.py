"""Placeholder desktop/window controller for future Linux integration."""

from __future__ import annotations


class DesktopController:
    def summon_window(self, name: str) -> dict[str, str]:
        return {"status": "placeholder", "message": f"Would summon window: {name}"}

    def hide_window(self, name: str) -> dict[str, str]:
        return {"status": "placeholder", "message": f"Would hide window: {name}"}
