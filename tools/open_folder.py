"""Safe folder opener for known user directories."""

from __future__ import annotations

import subprocess
from pathlib import Path

ALLOWED_FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "desktop": Path.home() / "Desktop",
    "home": Path.home(),
}


def open_folder(folder_name: str) -> dict[str, object]:
    key = folder_name.strip().lower()
    if key not in ALLOWED_FOLDERS:
        return {"status": "error", "tool": "open_folder", "message": f"Folder '{folder_name}' is not allowed."}

    path = ALLOWED_FOLDERS[key].expanduser().resolve()
    if not path.exists():
        return {"status": "error", "tool": "open_folder", "message": f"Folder does not exist: {path}"}

    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"status": "success", "tool": "open_folder", "message": f"Opening {path}.", "data": {"path": str(path)}}
