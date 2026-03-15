"""Package installation preview tool (no execution in V1)."""

from __future__ import annotations

import shutil


def _command_preview(package: str) -> str:
    if shutil.which("pacman"):
        return f"sudo pacman -S --needed {package}"
    if shutil.which("apt"):
        return f"sudo apt install -y {package}"
    if shutil.which("dnf"):
        return f"sudo dnf install -y {package}"
    if shutil.which("zypper"):
        return f"sudo zypper install -y {package}"
    return f"<package-manager> install {package}"


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
            "command_preview": _command_preview(safe_package),
        },
    }
