"""Safe application launcher using a strict allowlist."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterable

ALLOWED_APPS = {
    "firefox",
    "google-chrome",
    "chromium",
    "x-terminal-emulator",
    "gnome-terminal",
    "code",
}


def open_app(app_name: str, allowed_apps: Iterable[str] | None = None) -> dict[str, object]:
    app = app_name.strip().lower()
    allowlist = {item.strip().lower() for item in allowed_apps} if allowed_apps is not None else ALLOWED_APPS
    if app not in allowlist:
        return {"status": "error", "tool": "open_app", "message": f"App '{app}' is not in the allowlist."}

    binary = shutil.which(app)
    if not binary:
        return {"status": "error", "tool": "open_app", "message": f"App '{app}' is not installed."}

    subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"status": "success", "tool": "open_app", "message": f"Opening {app}.", "data": {"app": app}}
