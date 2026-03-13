"""Package installation preview tool (no execution in V1)."""

from __future__ import annotations


def prepare_install(package: str) -> dict[str, object]:
    cleaned = package.strip()
    if not cleaned:
        return {
            "status": "error",
            "tool": "install_package",
            "message": "No package name provided.",
        }

    safe_package = cleaned.split()[0]
    return {
        "status": "success",
        "tool": "install_package",
        "message": f"Installation requires confirmation for '{safe_package}'.",
        "data": {
            "requires_confirmation": True,
            "command_preview": f"sudo apt install -y {safe_package}",
            "package": safe_package,
        },
    }
