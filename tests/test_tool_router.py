from ai_core.tool_router import ToolRouter


def test_known_tool_returns_structured_result() -> None:
    router = ToolRouter()
    result = router.route({"tool": "install_package", "args": {"package": "numpy"}})
    assert result["status"] == "success"
    assert result["tool"] == "install_package"


def test_unknown_tool_returns_error() -> None:
    router = ToolRouter()
    result = router.route({"tool": "does_not_exist", "args": {}})
    assert result["status"] == "error"


def test_router_exposes_tool_metadata_lists() -> None:
    router = ToolRouter()
    assert "install_package" in router.list_tools()
    assert "list_windows" in router.list_tools()
    assert "install_package" in router.tools_requiring_confirmation()
    assert "close_window" in router.tools_requiring_confirmation()
    assert router.tool_permissions()["open_app"] == "read"
