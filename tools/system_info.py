"""System usage helpers powered by psutil when available."""

from __future__ import annotations

import importlib
import importlib.util

_PSUTIL_AVAILABLE = importlib.util.find_spec("psutil") is not None
_psutil = importlib.import_module("psutil") if _PSUTIL_AVAILABLE else None


def cpu_usage() -> dict[str, float | str]:
    if _psutil is None:
        return {"error": "psutil not installed"}
    return {"cpu_percent": _psutil.cpu_percent(interval=0.2)}


def memory_usage() -> dict[str, float | str]:
    if _psutil is None:
        return {"error": "psutil not installed"}
    vm = _psutil.virtual_memory()
    return {"memory_percent": vm.percent, "used_gb": round(vm.used / (1024**3), 2), "total_gb": round(vm.total / (1024**3), 2)}


def storage_usage() -> dict[str, float | str]:
    if _psutil is None:
        return {"error": "psutil not installed"}
    disk = _psutil.disk_usage("/")
    return {"storage_percent": disk.percent, "used_gb": round(disk.used / (1024**3), 2), "total_gb": round(disk.total / (1024**3), 2)}
