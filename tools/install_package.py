"""Safe package install wrapper with deny-by-default behavior."""

from __future__ import annotations

ALLOWED_PACKAGES = {"htop", "curl", "git"}


def run(package_name: str) -> str:
    package = package_name.strip().split()[0]
    if package not in ALLOWED_PACKAGES:
        return f"Blocked package '{package}'. Allowed: {sorted(ALLOWED_PACKAGES)}"

    # Prototype behavior: only simulate installation for safety.
    return f"[dry-run] Would install package: {package}"
