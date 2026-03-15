from security.confirmation_manager import ConfirmationManager


def test_requires_confirmation_for_configured_tool() -> None:
    manager = ConfirmationManager(required_tools=["install_package"], enabled=True)
    assert manager.requires_confirmation("install_package") is True
    assert manager.requires_confirmation("open_app") is False


def test_queue_confirm_and_clear_pending() -> None:
    manager = ConfirmationManager(required_tools=["install_package"], enabled=True)
    command = {"tool": "install_package", "args": {"package": "numpy"}}
    manager.queue(command)
    assert manager.has_pending() is True
    confirmed = manager.confirm()
    assert confirmed == command
    assert manager.has_pending() is False


def test_deny_clears_pending() -> None:
    manager = ConfirmationManager(required_tools=["install_package"], enabled=True)
    command = {"tool": "install_package", "args": {"package": "numpy"}}
    manager.queue(command)
    denied = manager.deny()
    assert denied == command
    assert manager.has_pending() is False


def test_disabled_confirmation_never_requires_confirmation() -> None:
    manager = ConfirmationManager(required_tools=["install_package"], enabled=False)
    assert manager.requires_confirmation("install_package") is False
