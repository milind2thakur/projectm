"""Simple sandbox abstraction for safe tool calls."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class SandboxRunner:
    """Runs approved Python tool callables.

    Future integration point: wrap this call in bubblewrap/firejail to isolate tools.
    """

    def run(self, func: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        return func()
