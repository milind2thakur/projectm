"""Package installation preview tool (no execution in V1)."""

from __future__ import annotations


def prepare_install(package: str) -> dict[str, object]:
    safe_package = package.strip().split()[0]
    if not safe_package:
        return {"status": "error", "tool": "install_package", "message": "Package name is required."}
    return {
        "status": "success",
        "tool": "install_package",
        "message": "Installation requires explicit confirmation.",
        "data": {
            "requires_confirmation": True,
            "command_preview": f"sudo apt install -y {safe_package}",
        },
    }
