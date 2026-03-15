"""Execution helper for workflow templates."""

from __future__ import annotations

from typing import Any, Callable

from .workflow_templates import WorkflowTemplateEngine


def run_workflow_template(
    template_name: str,
    workflow_engine: WorkflowTemplateEngine,
    execute_step: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    template = workflow_engine.get_template(template_name)
    if template is None:
        return {
            "status": "error",
            "tool": "workflow_run",
            "message": f"Unknown workflow '{template_name}'.",
        }

    step_results: list[dict[str, Any]] = []
    success_count = 0
    for step in template.steps:
        result = execute_step(step)
        step_results.append(
            {
                "tool": str(step.get("tool", "unknown")),
                "status": str(result.get("status", "error")),
                "message": str(result.get("message", "")),
            }
        )
        if result.get("status") == "success":
            success_count += 1

    total_steps = len(template.steps)
    if success_count == total_steps:
        status = "success"
    elif success_count > 0:
        status = "warning"
    else:
        status = "error"

    return {
        "status": status,
        "tool": "workflow_run",
        "message": f"Workflow '{template.name}' finished: {success_count}/{total_steps} successful steps.",
        "data": {
            "template": template.name,
            "total_steps": total_steps,
            "successful_steps": success_count,
            "steps": step_results,
        },
    }
