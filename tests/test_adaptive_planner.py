from ai_core.adaptive_planner import AdaptivePlanner
from ai_core.memory_engine import MemoryEngine


def test_generate_plan_from_goal(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    planner = AdaptivePlanner(memory)

    result = planner.generate_plan("Build coding prototype")

    assert result["status"] == "success"
    assert result["data"]["total_steps"] >= 3
    status = planner.status_report()
    assert status["status"] == "success"
    assert status["remaining_steps"] == status["total_steps"]


def test_plan_progress_updates(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    planner = AdaptivePlanner(memory)
    planner.generate_plan("System health validation")

    planner.set_next_step_index(2)
    status = planner.status_report()

    assert status["completed_steps"] == 2
    assert status["remaining_steps"] >= 1


def test_clear_plan(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    planner = AdaptivePlanner(memory)
    planner.generate_plan("Research mode")

    clear_result = planner.clear_plan()

    assert clear_result["status"] == "success"
    assert planner.has_active_plan() is False
