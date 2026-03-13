"""Text-to-speech placeholder with optional pyttsx3 backend."""

from __future__ import annotations

import importlib
import importlib.util


class TextToSpeech:
    def __init__(self) -> None:
        self.available = importlib.util.find_spec("pyttsx3") is not None
        self._engine = importlib.import_module("pyttsx3").init() if self.available else None

    def speak(self, text: str) -> dict[str, object]:
        if not self.available or self._engine is None:
            return {"status": "noop", "message": "pyttsx3 not configured.", "text": text}
        self._engine.say(text)
        self._engine.runAndWait()
        return {"status": "success", "message": "Spoken via pyttsx3.", "text": text}
