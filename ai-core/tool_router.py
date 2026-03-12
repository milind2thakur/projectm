"""Maps interpreted actions to concrete system tools."""

from __future__ import annotations

from typing import Callable, Dict

from tools.file_search import run as file_search
from tools.install_package import run as install_package
from tools.open_app import run as open_app
from tools.open_folder import run as open_folder
from tools.system_info import run as system_info


class ToolRouter:
    """Selects and executes tools based on interpreted action text."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[str], str]] = {
            "open folder": open_folder,
            "open app": open_app,
            "search file": file_search,
            "show system info": system_info,
            "install package": install_package,
        }

    def route_and_execute(self, interpreted_action: str) -> str:
        action = interpreted_action.strip().lower()

        if action.startswith("open "):
            target = action.replace("open ", "", 1)
            # Heuristic: folders are common paths/locations, apps are single program names.
            if any(token in target for token in ["/", "downloads", "documents", "desktop", "home"]):
                return self._tools["open folder"](target)
            return self._tools["open app"](target)

        if action.startswith("search file "):
            query = action.replace("search file ", "", 1)
            return self._tools["search file"](query)

        if action.startswith("show system info"):
            return self._tools["show system info"]("")

        if action.startswith("install package "):
            package = action.replace("install package ", "", 1)
            return self._tools["install package"](package)

        return f"No tool matched for action: {interpreted_action}"
