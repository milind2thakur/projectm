"""Command interpreter backed by llama-cpp-python with deterministic fallback."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from memory_engine import MemoryEngine
from prompt_engine import build_command_prompt

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover - optional runtime dependency
    Llama = None  # type: ignore


class CommandInterpreter:
    """Interprets natural language into structured tool calls."""

    def __init__(
        self,
        memory: Optional[MemoryEngine] = None,
        model_path: str = "models/projectm.gguf",
    ) -> None:
        self.memory = memory or MemoryEngine()
        self.model_path = model_path
        self._llm = self._load_llm(model_path)

    def _load_llm(self, model_path: str):
        if Llama is None:
            return None
        if not Path(model_path).exists():
            return None
        return Llama(model_path=model_path, n_ctx=2048, verbose=False)

    def interpret(self, user_command: str) -> dict[str, Any]:
        """Convert a user command into a structured tool-call dictionary."""
        tool_call = self._rule_based_fallback(user_command)

        if self._llm is not None:
            prompt = build_command_prompt(user_command)
            try:
                result = self._llm(
                    prompt,
                    max_tokens=96,
                    temperature=0.0,
                    stop=["\n\n"],
                )
                text = result["choices"][0]["text"].strip()
                parsed = self._parse_json_tool_call(text)
                if parsed is not None:
                    tool_call = parsed
            except Exception:
                # Keep deterministic fallback if local model invocation fails.
                pass

        self.memory.add(user_command=user_command, interpretation=json.dumps(tool_call))
        return tool_call

    def _parse_json_tool_call(self, content: str) -> Optional[dict[str, Any]]:
        candidate = content.strip()
        if not candidate:
            return None

        if "{" in candidate and "}" in candidate:
            candidate = candidate[candidate.find("{") : candidate.rfind("}") + 1]

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return None

        if not isinstance(parsed, dict) or not isinstance(parsed.get("tool"), str):
            return None

        tool_name = parsed["tool"].strip().lower()
        if tool_name not in {
            "open_folder",
            "open_app",
            "file_search",
            "system_info",
            "install_package",
            "unknown",
        }:
            return None

        parsed["tool"] = tool_name
        return parsed

    @staticmethod
    def _rule_based_fallback(user_command: str) -> dict[str, Any]:
        text = re.sub(r"\s+", " ", user_command.strip().lower())

        folder_map = {
            "downloads": "~/Downloads",
            "documents": "~/Documents",
            "desktop": "~/Desktop",
            "home": "~",
        }

        if text.startswith("open "):
            target = text.replace("open ", "", 1).strip()
            target = target.removesuffix(" folder").strip()

            if target in folder_map:
                return {"tool": "open_folder", "path": folder_map[target]}
            if target.startswith(("~/", "/", "./", "../")):
                return {"tool": "open_folder", "path": target}
            return {"tool": "open_app", "app_name": target}

        if text.startswith("find ") or text.startswith("search "):
            query = text.split(" ", 1)[1].strip()
            return {"tool": "file_search", "query": query}

        if "system info" in text or text == "info":
            return {"tool": "system_info"}

        if text.startswith("install "):
            package = text.replace("install ", "", 1).replace("package ", "", 1).strip()
            return {"tool": "install_package", "package": package}

        return {"tool": "unknown", "raw": text}
