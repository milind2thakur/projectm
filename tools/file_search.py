"""Simple safe file search limited to user's home directory."""

from __future__ import annotations

from pathlib import Path


MAX_RESULTS = 5


def run(query: str) -> str:
    root = Path.home()
    needle = query.strip().lower()
    if not needle:
        return "Please provide a filename query."

    results = []
    for path in root.rglob("*"):
        if len(results) >= MAX_RESULTS:
            break
        if needle in path.name.lower():
            results.append(str(path))

    if not results:
        return f"No files found for query: {query}"
    return "Found files:\n" + "\n".join(results)
