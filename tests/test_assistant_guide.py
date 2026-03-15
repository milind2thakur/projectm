from ai_core.assistant_guide import AssistantGuide
from ai_core.memory_engine import MemoryEngine


def test_suggest_next_for_empty_history(tmp_path) -> None:
    guide = AssistantGuide()
    memory = MemoryEngine(db_path=tmp_path / "memory.db")

    suggestions = guide.suggest_next(memory=memory, pending_command=None, limit=3)

    assert suggestions == ["open coding workspace", "show cpu usage", "list workflows"]


def test_suggest_next_for_pending_confirmation(tmp_path) -> None:
    guide = AssistantGuide()
    memory = MemoryEngine(db_path=tmp_path / "memory.db")

    suggestions = guide.suggest_next(
        memory=memory,
        pending_command={"tool": "install_package", "args": {"package": "numpy"}},
        limit=3,
    )

    assert suggestions[0] == "confirm"
    assert suggestions[1] == "deny"
    assert "install_package" in suggestions[2]


def test_suggest_next_after_system_info_success(tmp_path) -> None:
    guide = AssistantGuide()
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    memory.add_entry(
        {"raw_command": "show cpu usage", "tool": "system_info", "args": {"metric": "cpu"}},
        {"status": "success", "tool": "system_info", "message": "Retrieved cpu usage."},
    )

    suggestions = guide.suggest_next(memory=memory, pending_command=None, limit=3)

    assert suggestions[0] == "summarize system health"
    assert "list windows" in suggestions


def test_suggest_next_prefers_goal_actions_when_goal_is_active(tmp_path) -> None:
    guide = AssistantGuide()
    memory = MemoryEngine(db_path=tmp_path / "memory.db")

    suggestions = guide.suggest_next(
        memory=memory,
        pending_command=None,
        active_goal="Finish coding workflow",
        limit=3,
    )

    assert suggestions[0] == "plan goal"
    assert "goal status" in suggestions
    assert "open coding workspace" in suggestions


def test_suggest_next_prefers_plan_run_when_plan_exists(tmp_path) -> None:
    guide = AssistantGuide()
    memory = MemoryEngine(db_path=tmp_path / "memory.db")

    suggestions = guide.suggest_next(
        memory=memory,
        pending_command=None,
        active_goal="Finish coding workflow",
        has_active_plan=True,
        limit=3,
    )

    assert suggestions[0] == "plan run"
    assert "plan show" in suggestions
