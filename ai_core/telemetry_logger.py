"""JSONL telemetry logger for runtime events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4


class TelemetryLogger:
    """Writes structured runtime telemetry events to JSONL."""

    def __init__(
        self,
        enabled: bool = True,
        log_path: str | Path = "logs/projectm_events.jsonl",
        session_id: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or str(uuid4())
        self._lock = Lock()

    def log_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        if not self.enabled:
            return
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "payload": payload or {},
        }
        line = json.dumps(event, ensure_ascii=True)
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
