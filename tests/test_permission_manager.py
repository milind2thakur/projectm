from security.permission_manager import PermissionManager


def test_read_level_allows_open_app() -> None:
    manager = PermissionManager()
    assert manager.can_execute("open_app", granted_level="read") is True


def test_install_package_requires_admin() -> None:
    manager = PermissionManager()
    assert manager.can_execute("install_package", granted_level="read") is False
    assert manager.can_execute("install_package", granted_level="admin") is True
