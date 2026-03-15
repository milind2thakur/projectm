from security.sandbox_runner import SandboxRunner


def test_sandbox_returns_error_when_tool_raises() -> None:
    runner = SandboxRunner()

    def _boom() -> dict[str, str]:
        raise RuntimeError("boom")

    result = runner.run(_boom)
    assert result["status"] == "error"
    assert result["tool"] == "sandbox"
    assert "boom" in result["message"]
