"""Filename-only local file search."""

from __future__ import annotations

import os
from pathlib import Path


MAX_RESULTS = 20


def search_files(query: str, root: Path | None = None) -> dict[str, object]:
    needle = query.strip().lower()
    if not needle:
        return {"status": "error", "tool": "file_search", "message": "Search query cannot be empty."}

    search_root = (root or Path.home()).expanduser()
    matches: list[str] = []

    for current_root, _, files in os.walk(search_root):
        for name in files:
            if needle in name.lower():
                matches.append(str(Path(current_root) / name))
                if len(matches) >= MAX_RESULTS:
                    return {
                        "status": "success",
                        "tool": "file_search",
                        "message": f"Found {len(matches)} matches (capped).",
                        "data": {"results": matches},
                    }

    return {
        "status": "success",
        "tool": "file_search",
        "message": f"Found {len(matches)} matches.",
        "data": {"results": matches},
    }
