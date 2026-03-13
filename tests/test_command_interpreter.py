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
