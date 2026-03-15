from ai_core.memory_engine import MemoryEngine
from main import print_terminal_help, print_terminal_history


def test_print_terminal_help_includes_core_commands(capsys) -> None:
    print_terminal_help()
    output = capsys.readouterr().out
    assert "help" in output
    assert "history [n]" in output
    assert "voice" in output
    assert "ptt" in output
    assert "confirm" in output
    assert "deny" in output
    assert "resume" in output
    assert "list windows" in output
    assert "list workflows" in output
    assert "exit | quit" in output


def test_print_terminal_history_empty(capsys, tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    print_terminal_history(memory, limit=5)
    output = capsys.readouterr().out.strip()
    assert output == "No command history yet."


def test_print_terminal_history_with_entries(capsys, tmp_path) -> None:
    memory = MemoryEngine(db_path=tmp_path / "memory.db")
    memory.add_entry(
        {"raw_command": "show cpu usage", "tool": "system_info", "args": {"metric": "cpu"}},
        {"status": "success", "tool": "system_info", "message": "Retrieved cpu usage."},
    )
    memory.add_entry(
        {"raw_command": "open firefox", "tool": "open_app", "args": {"app": "firefox"}},
        {"status": "error", "tool": "open_app", "message": "App not installed."},
    )

    print_terminal_history(memory, limit=5)
    output = capsys.readouterr().out
    assert "1. show cpu usage -> success" in output
    assert "2. open firefox -> error" in output
