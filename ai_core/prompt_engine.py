"""Prompt helpers for Project M."""

from __future__ import annotations


def build_system_prompt(allowed_tools: list[str]) -> str:
    tool_list = ", ".join(allowed_tools)
    return (
        "You are Project M, an AI-first Linux desktop shell assistant. "
        "Interpret user commands and map them to one tool. "
        "Only use allowed tools: "
        f"{tool_list}. "
        "Return JSON with keys: tool, args, raw_command."
    )
