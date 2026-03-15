import json

from ai_core.telemetry_logger import TelemetryLogger


def test_telemetry_logger_writes_jsonl_event(tmp_path) -> None:
    log_path = tmp_path / "events.jsonl"
    telemetry = TelemetryLogger(enabled=True, log_path=log_path, session_id="session-test")
    telemetry.log_event("command_result", {"tool": "system_info", "status": "success"})

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["session_id"] == "session-test"
    assert event["event_type"] == "command_result"
    assert event["payload"]["tool"] == "system_info"


def test_telemetry_logger_noop_when_disabled(tmp_path) -> None:
    log_path = tmp_path / "events.jsonl"
    telemetry = TelemetryLogger(enabled=False, log_path=log_path, session_id="session-test")
    telemetry.log_event("command_result", {"tool": "system_info"})
    assert not log_path.exists()
