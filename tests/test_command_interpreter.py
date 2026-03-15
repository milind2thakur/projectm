from ai_core.command_interpreter import CommandInterpreter


def test_fallback_open_firefox() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("open firefox")
    assert command["tool"] == "open_app"
    assert command["args"]["app"] == "firefox"


def test_fallback_install_package() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("install numpy")
    assert command == {
        "tool": "install_package",
        "args": {"package": "numpy"},
        "raw_command": "install numpy",
    }


def test_fallback_list_windows() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("list windows")
    assert command == {"tool": "list_windows", "args": {}, "raw_command": "list windows"}


def test_fallback_focus_window() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("focus firefox")
    assert command == {
        "tool": "focus_window",
        "args": {"target": "firefox"},
        "raw_command": "focus firefox",
    }


def test_fallback_list_workflows() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("list workflows")
    assert command == {"tool": "workflow_list", "args": {}, "raw_command": "list workflows"}


def test_fallback_run_workflow() -> None:
    interpreter = CommandInterpreter(model_path=None)
    command = interpreter.interpret("run workflow coding workspace")
    assert command == {
        "tool": "workflow_run",
        "args": {"template": "coding_workspace"},
        "raw_command": "run workflow coding workspace",
    }
