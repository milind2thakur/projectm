"""Linux window management helpers using wmctrl."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


def _ensure_wmctrl() -> str | None:
    return shutil.which("wmctrl")


def _run_wmctrl(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=False)


def _parse_windows(output: str) -> list[dict[str, str]]:
    windows: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            continue
        win_id, desktop, host, title = parts
        windows.append({"id": win_id, "desktop": desktop, "host": host, "title": title})
    return windows


def list_windows() -> dict[str, Any]:
    wmctrl = _ensure_wmctrl()
    if wmctrl is None:
        return {
            "status": "error",
            "tool": "list_windows",
            "message": "wmctrl is not installed. Install it to manage windows.",
        }

    proc = _run_wmctrl([wmctrl, "-l"])
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or "wmctrl failed to list windows."
        return {"status": "error", "tool": "list_windows", "message": stderr}

    windows = _parse_windows(proc.stdout)
    return {
        "status": "success",
        "tool": "list_windows",
        "message": f"Found {len(windows)} window(s).",
        "data": {"windows": windows},
    }


def _find_window_id(query: str) -> tuple[str | None, str | None]:
    listed = list_windows()
    if listed.get("status") != "success":
        return None, str(listed.get("message", "Unable to list windows."))
    windows = listed.get("data", {}).get("windows", [])
    if not isinstance(windows, list):
        return None, "Unable to parse window list."

    needle = query.strip().lower()
    if not needle:
        return None, "Window target is required."

    for win in windows:
        title = str(win.get("title", ""))
        if needle in title.lower():
            return str(win.get("id", "")), None
    return None, f"No matching window found for '{query}'."


def focus_window(target: str) -> dict[str, Any]:
    wmctrl = _ensure_wmctrl()
    if wmctrl is None:
        return {
            "status": "error",
            "tool": "focus_window",
            "message": "wmctrl is not installed. Install it to manage windows.",
        }
    win_id, error = _find_window_id(target)
    if error:
        return {"status": "error", "tool": "focus_window", "message": error}

    proc = _run_wmctrl([wmctrl, "-ia", str(win_id)])
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or "wmctrl failed to focus window."
        return {"status": "error", "tool": "focus_window", "message": stderr}
    return {
        "status": "success",
        "tool": "focus_window",
        "message": f"Focused window matching '{target}'.",
        "data": {"window_id": win_id},
    }


def minimize_window(target: str) -> dict[str, Any]:
    wmctrl = _ensure_wmctrl()
    if wmctrl is None:
        return {
            "status": "error",
            "tool": "minimize_window",
            "message": "wmctrl is not installed. Install it to manage windows.",
        }
    win_id, error = _find_window_id(target)
    if error:
        return {"status": "error", "tool": "minimize_window", "message": error}

    proc = _run_wmctrl([wmctrl, "-ir", str(win_id), "-b", "add,hidden"])
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or "wmctrl failed to minimize window."
        return {"status": "error", "tool": "minimize_window", "message": stderr}
    return {
        "status": "success",
        "tool": "minimize_window",
        "message": f"Minimized window matching '{target}'.",
        "data": {"window_id": win_id},
    }


def close_window(target: str) -> dict[str, Any]:
    wmctrl = _ensure_wmctrl()
    if wmctrl is None:
        return {
            "status": "error",
            "tool": "close_window",
            "message": "wmctrl is not installed. Install it to manage windows.",
        }
    win_id, error = _find_window_id(target)
    if error:
        return {"status": "error", "tool": "close_window", "message": error}

    proc = _run_wmctrl([wmctrl, "-ic", str(win_id)])
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or "wmctrl failed to close window."
        return {"status": "error", "tool": "close_window", "message": stderr}
    return {
        "status": "success",
        "tool": "close_window",
        "message": f"Closed window matching '{target}'.",
        "data": {"window_id": win_id},
    }
