"""Safe wrapper for opening desktop applications."""

from __future__ import annotations

import shutil
import subprocess

ALLOWED_APPS = {"code", "firefox", "gedit", "nautilus", "terminal"}


def run(app_name: str) -> str:
    app = app_name.strip().split()[0]
    if app not in ALLOWED_APPS:
        return f"Blocked app '{app}'. Allowed: {sorted(ALLOWED_APPS)}"

    binary = shutil.which(app)
    if not binary:
        return f"Application '{app}' is not installed."

    try:
        subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening app: {app}"
    except Exception as exc:
        return f"Failed to open app '{app}': {exc}"
