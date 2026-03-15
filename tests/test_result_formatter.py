from ui.result_formatter import format_status_message


def test_format_install_preview_message() -> None:
    message = format_status_message(
        {
            "tool": "install_package",
            "message": "Installation requires explicit confirmation.",
            "data": {"command_preview": "sudo pacman -S --needed numpy"},
        }
    )
    assert "sudo pacman -S --needed numpy" in message


def test_format_system_cpu_message() -> None:
    message = format_status_message(
        {
            "tool": "system_info",
            "message": "Retrieved cpu usage.",
            "data": {"cpu_percent": 15.3},
        }
    )
    assert message == "CPU usage: 15.3%"


def test_format_file_search_message() -> None:
    message = format_status_message(
        {
            "tool": "file_search",
            "message": "Found 2 matches.",
            "data": {"results": ["/tmp/a.txt", "/tmp/b.txt"]},
        }
    )
    assert message == "Found 2 matches. Showing 2 result(s)."
