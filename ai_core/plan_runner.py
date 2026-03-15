"""Execution helper for adaptive plans with pause/resume behavior."""

from __future__ import annotations

from typing import Any, Callable


def run_plan_steps(
    plan: dict[str, Any],
    execute_step: Callable[[dict[str, Any]], dict[str, Any]],
    start_index: int = 0,
) -> dict[str, Any]:
    steps = plan.get("steps", [])
    if not isinstance(steps, list):
        return {"status": "error", "tool": "plan_run", "message": "Invalid plan format."}

    total_steps = len(steps)
    safe_start = min(max(0, int(start_index)), total_steps)
    if total_steps == 0:
        return {
            "status": "warning",
            "tool": "plan_run",
            "message": "Plan has no steps to execute.",
            "data": {"total_steps": 0, "completed_steps": 0, "next_step_index": 0, "steps": []},
        }
    if safe_start >= total_steps:
        return {
            "status": "success",
            "tool": "plan_run",
            "message": "Plan already completed.",
            "data": {
                "total_steps": total_steps,
                "completed_steps": total_steps,
                "next_step_index": total_steps,
                "steps": [],
            },
        }

    executed: list[dict[str, Any]] = []
    next_step_index = safe_start
    for idx in range(safe_start, total_steps):
        step = steps[idx]
        result = execute_step(step)
        status = str(result.get("status", "error"))
        executed.append(
            {
                "index": idx + 1,
                "tool": str(step.get("tool", "unknown")),
                "status": status,
                "message": str(result.get("message", "")),
            }
        )
        if status == "success":
            next_step_index = idx + 1
            continue
        break

    completed_steps = next_step_index
    if next_step_index >= total_steps:
        status = "success"
        message = f"Plan completed successfully ({completed_steps}/{total_steps} step(s))."
    elif next_step_index == safe_start:
        status = "warning"
        message = f"Plan blocked at step {safe_start + 1}/{total_steps}."
    else:
        status = "warning"
        message = (
            f"Plan paused at step {next_step_index + 1}/{total_steps} "
            f"after completing {next_step_index - safe_start} step(s)."
        )

    return {
        "status": status,
        "tool": "plan_run",
        "message": message,
        "data": {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "next_step_index": next_step_index,
            "steps": executed,
        },
    }
