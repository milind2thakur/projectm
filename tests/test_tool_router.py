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
