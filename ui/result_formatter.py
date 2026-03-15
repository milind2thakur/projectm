"""Helpers to render concise, human-friendly status lines."""

from __future__ import annotations

from typing import Any


def format_status_message(result: dict[str, Any]) -> str:
    message = str(result.get("message", "No message"))
    data = result.get("data")
    tool = str(result.get("tool", ""))

    if not isinstance(data, dict):
        return message

    if tool == "install_package" and "command_preview" in data:
        return f"{message} ({data['command_preview']})"

    if tool == "file_search":
        results = data.get("results")
        if isinstance(results, list):
            return f"{message} Showing {len(results)} result(s)."
        return message

    if tool == "list_windows":
        windows = data.get("windows")
        if isinstance(windows, list):
            return f"{message} Showing {len(windows)} window(s)."
        return message

    if tool == "workflow_list":
        workflows = data.get("workflows")
        if isinstance(workflows, list):
            return f"{message} Showing {len(workflows)} workflow(s)."
        return message

    if tool == "workflow_run":
        if {"successful_steps", "total_steps"}.issubset(data):
            return (
                f"{message} "
                f"({data['successful_steps']}/{data['total_steps']} step(s) succeeded)"
            )
        return message

    if tool == "system_info":
        if "cpu_percent" in data:
            return f"CPU usage: {data['cpu_percent']}%"
        if {"memory_percent", "used_gb", "total_gb"}.issubset(data):
            return (
                f"Memory usage: {data['memory_percent']}% "
                f"({data['used_gb']} GB / {data['total_gb']} GB)"
            )
        if {"storage_percent", "used_gb", "total_gb"}.issubset(data):
            return (
                f"Storage usage: {data['storage_percent']}% "
                f"({data['used_gb']} GB / {data['total_gb']} GB)"
            )

    return message
