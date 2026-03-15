from ai_core.tool_registry import ToolRegistry, ToolSpec, build_default_registry


def test_registry_executes_registered_tool() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="ping",
            description="test tool",
            handler=lambda args: {"status": "success", "tool": "ping", "data": args},
        )
    )
    result = registry.execute("ping", {"value": 1})
    assert result["status"] == "success"
    assert result["tool"] == "ping"
    assert result["data"] == {"value": 1}


def test_registry_unknown_tool_returns_error() -> None:
    registry = ToolRegistry()
    result = registry.execute("does_not_exist", {})
    assert result["status"] == "error"
    assert "Unknown tool" in result["message"]


def test_default_registry_exposes_policy_metadata() -> None:
    registry = build_default_registry()
    assert "install_package" in registry.tools_requiring_confirmation()
    assert "close_window" in registry.tools_requiring_confirmation()
    permissions = registry.tool_permissions()
    assert permissions["open_app"] == "read"
    assert "workflow_list" in registry.list_tool_names()
