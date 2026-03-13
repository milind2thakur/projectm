"""Tkinter orb renderer with stateful glow and pulse animation."""

from __future__ import annotations

import tkinter as tk


class OrbRenderer:
    """Draws and animates the Project M orb."""

    STATE_COLORS = {
        "idle": "#3b82f6",       # blue
        "listening": "#a855f7",  # purple
        "thinking": "#f59e0b",   # orange
        "executing": "#22c55e",  # green
    }

    def __init__(self, canvas: tk.Canvas, center_x: int = 250, center_y: int = 180, radius: int = 42) -> None:
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.base_radius = radius
        self.state = "idle"
        self._pulse_step = 0

        self._glow = self.canvas.create_oval(0, 0, 0, 0, fill="#1d4ed8", outline="")
        self._orb = self.canvas.create_oval(0, 0, 0, 0, fill="#3b82f6", outline="")

        self._draw_orb(radius, self.STATE_COLORS[self.state])
        self._animate()

    def set_state(self, state: str) -> None:
        if state in self.STATE_COLORS:
            self.state = state

    def _draw_orb(self, radius: int, color: str) -> None:
        glow_radius = int(radius * 1.8)
        glow_color = self._dim_color(color, 0.25)

        self.canvas.coords(
            self._glow,
            self.center_x - glow_radius,
            self.center_y - glow_radius,
            self.center_x + glow_radius,
            self.center_y + glow_radius,
        )
        self.canvas.itemconfig(self._glow, fill=glow_color)

        self.canvas.coords(
            self._orb,
            self.center_x - radius,
            self.center_y - radius,
            self.center_x + radius,
            self.center_y + radius,
        )
        self.canvas.itemconfig(self._orb, fill=color)

    @staticmethod
    def _dim_color(hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(int(hex_color[0:2], 16) * factor)
        g = int(int(hex_color[2:4], 16) * factor)
        b = int(int(hex_color[4:6], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _animate(self) -> None:
        self._pulse_step = (self._pulse_step + 1) % 30
        pulse = 3 if self._pulse_step < 15 else 0

        color = self.STATE_COLORS.get(self.state, self.STATE_COLORS["idle"])
        self._draw_orb(self.base_radius + pulse, color)
        self.canvas.after(60, self._animate)
