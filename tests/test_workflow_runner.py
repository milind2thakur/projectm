from ai_core.workflow_runner import run_workflow_template
from ai_core.workflow_templates import WorkflowTemplateEngine


def test_workflow_runner_success_path() -> None:
    engine = WorkflowTemplateEngine()

    def _exec(_command):
        return {"status": "success", "message": "ok"}

    result = run_workflow_template("system_health", engine, _exec)
    assert result["status"] == "success"
    assert result["tool"] == "workflow_run"
    assert result["data"]["total_steps"] == 3
    assert result["data"]["successful_steps"] == 3


def test_workflow_runner_unknown_template() -> None:
    engine = WorkflowTemplateEngine()
    result = run_workflow_template("missing_template", engine, lambda _cmd: {"status": "success"})
    assert result["status"] == "error"
    assert "Unknown workflow" in result["message"]
