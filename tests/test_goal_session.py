from ai_core.goal_session import GoalSessionManager
from ai_core.memory_engine import MemoryEngine


def test_goal_session_set_and_get_active_goal(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    goals = GoalSessionManager(memory)

    result = goals.set_goal("Finish coding workspace prototype")

    assert result["status"] == "success"
    assert goals.get_active_goal() == "Finish coding workspace prototype"


def test_goal_session_status_report_counts_tasks(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    goals = GoalSessionManager(memory)
    goals.set_goal("System health pass")
    memory.add_entry(
        {"raw_command": "show cpu usage", "tool": "system_info", "args": {"metric": "cpu"}},
        {"status": "success", "tool": "system_info"},
    )
    memory.add_entry(
        {"raw_command": "install numpy", "tool": "install_package", "args": {"package": "numpy"}},
        {"status": "warning", "tool": "install_package"},
    )
    memory.add_entry(
        {"raw_command": "open unknown", "tool": "open_app", "args": {"app": "unknown"}},
        {"status": "error", "tool": "open_app"},
    )

    status = goals.status_report()

    assert status["status"] == "success"
    assert status["tasks_total"] == 3
    assert status["tasks_success"] == 1
    assert status["tasks_warning"] == 1
    assert status["tasks_error"] == 1
    assert "show cpu usage" in status["recent"]


def test_goal_session_clear(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    goals = GoalSessionManager(memory)
    goals.set_goal("Clean up backlog")

    clear_result = goals.clear_goal()

    assert clear_result["status"] == "success"
    assert goals.get_active_goal() is None
