"""Prompt construction helpers for Project M."""

from __future__ import annotations


def build_command_prompt(user_command: str) -> str:
    """Build a lightweight prompt for command understanding."""
    return (
        "You are Project M, an AI-native OS assistant. "
        "Extract the intent and target from the user's command and return a concise action phrase. "
        f"User command: {user_command}"
    )
