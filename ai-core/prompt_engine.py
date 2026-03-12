"""Prompt construction helpers for Project M."""

from __future__ import annotations


def build_command_prompt(user_command: str) -> str:
    """Build a lightweight prompt for command understanding."""
    return (
        "You are Project M, an AI-native OS assistant. "
        "Convert the user command into exactly one JSON object with keys 'tool' and optional arguments. "
        "Allowed tools: open_folder(path), open_app(app_name), file_search(query), system_info(), install_package(package). "
        "Respond with JSON only. "
        "Example input: open downloads. "
        "Example output: {\"tool\": \"open_folder\", \"path\": \"~/Downloads\"}. "
        f"User command: {user_command}"
    )
