from ai_core.workflow_templates import WorkflowTemplateEngine


def test_workflow_engine_lists_default_workflows() -> None:
    engine = WorkflowTemplateEngine()
    names = [item["name"] for item in engine.list_workflows()]
    assert "coding_workspace" in names
    assert "system_health" in names


def test_workflow_engine_resolves_aliases() -> None:
    engine = WorkflowTemplateEngine()
    template = engine.get_template("start coding workflow")
    assert template is not None
    assert template.name == "coding_workspace"
