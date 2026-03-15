import subprocess

from tools import window_control


def test_list_windows_requires_wmctrl(monkeypatch) -> None:
    monkeypatch.setattr(window_control, "_ensure_wmctrl", lambda: None)
    result = window_control.list_windows()
    assert result["status"] == "error"
    assert "wmctrl is not installed" in result["message"]


def test_list_windows_parses_wmctrl_output(monkeypatch) -> None:
    monkeypatch.setattr(window_control, "_ensure_wmctrl", lambda: "wmctrl")

    def _fake_run(_args):
        return subprocess.CompletedProcess(
            args=["wmctrl", "-l"],
            returncode=0,
            stdout="0x01200003  0 host Firefox\n0x03400007  0 host Terminal\n",
            stderr="",
        )

    monkeypatch.setattr(window_control, "_run_wmctrl", _fake_run)
    result = window_control.list_windows()
    assert result["status"] == "success"
    assert result["data"]["windows"][0]["title"] == "Firefox"


def test_focus_window_no_match_returns_error(monkeypatch) -> None:
    monkeypatch.setattr(window_control, "_ensure_wmctrl", lambda: "wmctrl")
    monkeypatch.setattr(
        window_control,
        "list_windows",
        lambda: {
            "status": "success",
            "tool": "list_windows",
            "message": "ok",
            "data": {"windows": [{"id": "0x01", "title": "Firefox"}]},
        },
    )
    result = window_control.focus_window("code")
    assert result["status"] == "error"
    assert "No matching window" in result["message"]
