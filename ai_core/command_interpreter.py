"""Command interpretation with optional llama.cpp support and safe fallback parsing."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from .prompt_engine import build_system_prompt


class CommandInterpreter:
    """Interprets free-form user input into a structured tool command."""

    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self.allowed_tools = [
            "open_app",
            "open_folder",
            "system_info",
            "install_package",
            "file_search",
            "list_windows",
            "focus_window",
            "minimize_window",
            "close_window",
            "workflow_list",
            "workflow_run",
        ]
        self._llm = self._init_optional_llm()
        self.mode = "model" if self._llm is not None else "fallback"

    def _init_optional_llm(self) -> Any | None:
        if not self.model_path:
            return None
        model_file = Path(self.model_path).expanduser()
        if not model_file.exists():
            return None
        if importlib.util.find_spec("llama_cpp") is None:
            return None
        llama_module = importlib.import_module("llama_cpp")
        return llama_module.Llama(model_path=str(model_file), n_ctx=2048, verbose=False)

    def interpret(self, user_text: str) -> dict[str, Any]:
        if self._llm is not None:
            model_result = self._interpret_with_model(user_text)
            if model_result:
                return model_result
        return self._interpret_fallback(user_text)

    def _interpret_with_model(self, user_text: str) -> dict[str, Any] | None:
        prompt = build_system_prompt(self.allowed_tools) + f"\nUser: {user_text}\nAssistant:"
        result = self._llm(prompt, max_tokens=180, temperature=0.0)
        text = result["choices"][0]["text"].strip()
        if not text:
            return None
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return {
            "tool": str(data.get("tool", "unknown")),
            "args": data.get("args", {}) if isinstance(data.get("args", {}), dict) else {},
            "raw_command": user_text,
        }

    def _interpret_fallback(self, user_text: str) -> dict[str, Any]:
        text = re.sub(r"\s+", " ", user_text.strip().lower())

        app_aliases = {
            "firefox": "firefox",
            "chrome": "google-chrome",
            "google chrome": "google-chrome",
            "chromium": "chromium",
            "terminal": "x-terminal-emulator",
        }
        folder_aliases = {"downloads": "Downloads", "documents": "Documents", "desktop": "Desktop", "home": "Home"}

        if text.startswith("open "):
            target = text.removeprefix("open ").strip()
            if target in app_aliases:
                return {"tool": "open_app", "args": {"app": app_aliases[target]}, "raw_command": user_text}
            if target in folder_aliases:
                return {"tool": "open_folder", "args": {"folder": folder_aliases[target]}, "raw_command": user_text}
            if any(word in target for word in ["downloads", "documents", "desktop", "home"]):
                return {"tool": "open_folder", "args": {"folder": target.title()}, "raw_command": user_text}
            return {"tool": "open_app", "args": {"app": target}, "raw_command": user_text}

        if text in {"show cpu usage", "cpu usage", "show cpu"}:
            return {"tool": "system_info", "args": {"metric": "cpu"}, "raw_command": user_text}
        if text in {"show memory usage", "memory usage", "show memory"}:
            return {"tool": "system_info", "args": {"metric": "memory"}, "raw_command": user_text}
        if text in {"show storage usage", "storage usage", "show disk usage", "show storage"}:
            return {"tool": "system_info", "args": {"metric": "storage"}, "raw_command": user_text}

        if text.startswith("install "):
            package = text.removeprefix("install ").strip().split(" ")[0]
            return {"tool": "install_package", "args": {"package": package}, "raw_command": user_text}

        if text.startswith("find "):
            query = text.removeprefix("find ").strip()
            return {"tool": "file_search", "args": {"query": query}, "raw_command": user_text}

        if text in {"list windows", "show windows", "what windows are open"}:
            return {"tool": "list_windows", "args": {}, "raw_command": user_text}

        if text.startswith("focus window "):
            target = text.removeprefix("focus window ").strip()
            return {"tool": "focus_window", "args": {"target": target}, "raw_command": user_text}
        if text.startswith("focus "):
            target = text.removeprefix("focus ").strip()
            return {"tool": "focus_window", "args": {"target": target}, "raw_command": user_text}

        if text.startswith("minimize window "):
            target = text.removeprefix("minimize window ").strip()
            return {"tool": "minimize_window", "args": {"target": target}, "raw_command": user_text}
        if text.startswith("minimize "):
            target = text.removeprefix("minimize ").strip()
            return {"tool": "minimize_window", "args": {"target": target}, "raw_command": user_text}

        if text.startswith("close window "):
            target = text.removeprefix("close window ").strip()
            return {"tool": "close_window", "args": {"target": target}, "raw_command": user_text}
        if text.startswith("close "):
            target = text.removeprefix("close ").strip()
            return {"tool": "close_window", "args": {"target": target}, "raw_command": user_text}

        if text in {"list workflows", "workflow list", "show workflows"}:
            return {"tool": "workflow_list", "args": {}, "raw_command": user_text}

        if text.startswith("run workflow "):
            template = text.removeprefix("run workflow ").strip().replace(" ", "_")
            return {"tool": "workflow_run", "args": {"template": template}, "raw_command": user_text}
        if text.startswith("start workflow "):
            template = text.removeprefix("start workflow ").strip().replace(" ", "_")
            return {"tool": "workflow_run", "args": {"template": template}, "raw_command": user_text}

        if text in {"open coding workspace", "start coding workflow"}:
            return {"tool": "workflow_run", "args": {"template": "coding_workspace"}, "raw_command": user_text}
        if text in {"summarize system health", "system health summary"}:
            return {"tool": "workflow_run", "args": {"template": "system_health"}, "raw_command": user_text}

        return {"tool": "unknown", "args": {"text": text}, "raw_command": user_text}
