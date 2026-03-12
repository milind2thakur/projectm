"""Return basic system information without shell command execution."""

from __future__ import annotations

import platform


def run(_: str = "") -> str:
    return (
        f"System: {platform.system()}\n"
        f"Release: {platform.release()}\n"
        f"Version: {platform.version()}\n"
        f"Machine: {platform.machine()}"
    )
