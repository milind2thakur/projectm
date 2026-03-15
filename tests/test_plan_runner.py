from ai_core.plan_runner import run_plan_steps


def test_run_plan_steps_completes() -> None:
    plan = {
        "steps": [
            {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
            {"tool": "list_windows", "args": {}, "raw_command": "list windows"},
        ]
    }

    result = run_plan_steps(plan, lambda _step: {"status": "success", "message": "ok"}, start_index=0)

    assert result["status"] == "success"
    assert result["data"]["completed_steps"] == 2
    assert result["data"]["next_step_index"] == 2


def test_run_plan_steps_pauses_on_warning() -> None:
    plan = {
        "steps": [
            {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
            {"tool": "open_app", "args": {"app": "code"}, "raw_command": "open code"},
        ]
    }

    def _exec(step):
        if step["tool"] == "open_app":
            return {"status": "warning", "message": "blocked"}
        return {"status": "success", "message": "ok"}

    result = run_plan_steps(plan, _exec, start_index=0)

    assert result["status"] == "warning"
    assert result["data"]["completed_steps"] == 1
    assert result["data"]["next_step_index"] == 1
