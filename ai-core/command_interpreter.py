"""Command interpreter backed by llama-cpp-python with safe fallback mode."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from memory_engine import MemoryEngine
from prompt_engine import build_command_prompt

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover - optional runtime dependency
    Llama = None  # type: ignore


class CommandInterpreter:
    """Interprets natural language commands into actionable phrases."""

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

    def interpret(self, user_command: str) -> str:
        """Convert a user command into a simplified action statement."""
        prompt = build_command_prompt(user_command)
        interpretation = self._rule_based_fallback(user_command)

        if self._llm is not None:
            try:
                result = self._llm(
                    prompt,
                    max_tokens=64,
                    temperature=0.1,
                    stop=["\n"],
                )
                text = result["choices"][0]["text"].strip()
                if text:
                    interpretation = text
            except Exception:
                # Keep fallback interpretation in case local model invocation fails.
                pass

        self.memory.add(user_command=user_command, interpretation=interpretation)
        return interpretation

    @staticmethod
    def _rule_based_fallback(user_command: str) -> str:
        text = user_command.strip().lower()
        text = re.sub(r"\s+", " ", text)

        if text.startswith("open "):
            target = text.replace("open ", "", 1)
            if target.endswith(" folder"):
                target = target[: -len(" folder")].strip()
            return f"open {target}"
        if text.startswith("find "):
            target = text.replace("find ", "", 1)
            return f"search file {target}"
        if "system info" in text or text == "info":
            return "show system info"
        if text.startswith("install "):
            target = text.replace("install ", "", 1)
            return f"install package {target}"
        return f"unknown action: {text}"
