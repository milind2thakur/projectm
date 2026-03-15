from ai_core.memory_engine import MemoryEngine


def test_memory_engine_persists_entries(tmp_path) -> None:
    db_path = tmp_path / "memory.db"
    memory = MemoryEngine(db_path=db_path)
    memory.add_entry(
        {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": "show cpu usage"},
        {"status": "success", "tool": "system_info", "message": "Retrieved cpu usage."},
    )
    memory.close()

    memory2 = MemoryEngine(db_path=db_path)
    last = memory2.get_last_entry()
    assert last is not None
    assert last["command"]["tool"] == "system_info"
    assert last["result"]["status"] == "success"


def test_memory_engine_history_limit_order(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    memory.add_entry({"raw_command": "first"}, {"status": "success"})
    memory.add_entry({"raw_command": "second"}, {"status": "success"})
    memory.add_entry({"raw_command": "third"}, {"status": "success"})
    history = memory.get_history(limit=2)
    assert [entry["command"]["raw_command"] for entry in history] == ["second", "third"]


def test_memory_engine_state_round_trip(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")

    memory.set_state("active_goal_session", {"goal": "Ship demo", "start_entry_id": 2})
    state = memory.get_state("active_goal_session")

    assert isinstance(state, dict)
    assert state["goal"] == "Ship demo"
    memory.delete_state("active_goal_session")
    assert memory.get_state("active_goal_session") is None


def test_memory_engine_entries_since(tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    memory.add_entry({"raw_command": "one"}, {"status": "success"})
    marker = memory.get_last_entry_id()
    memory.add_entry({"raw_command": "two"}, {"status": "success"})
    memory.add_entry({"raw_command": "three"}, {"status": "warning"})

    entries = memory.get_entries_since(marker, limit=10)

    assert [entry["command"]["raw_command"] for entry in entries] == ["two", "three"]
