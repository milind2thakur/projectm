"""Safe wrapper for opening approved local folders."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ALLOWED_FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "desktop": Path.home() / "Desktop",
    "home": Path.home(),
}


def run(target: str) -> str:
    key = target.strip().lower()
    folder = ALLOWED_FOLDERS.get(key)

    if folder is None:
        # Allow explicit absolute paths under home directory.
        candidate = Path(target).expanduser().resolve()
        if str(candidate).startswith(str(Path.home().resolve())):
            folder = candidate
        else:
            return f"Blocked folder '{target}'. Use approved locations only."

    if not folder.exists() or not folder.is_dir():
        return f"Folder not found: {folder}"

    opener = "xdg-open" if os.name != "nt" else "explorer"
    try:
        subprocess.Popen([opener, str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening folder: {folder}"
    except Exception as exc:
        return f"Failed to open folder '{folder}': {exc}"
