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
