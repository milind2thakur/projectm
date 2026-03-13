"""Speech-to-text placeholder with optional faster-whisper detection."""

from __future__ import annotations

import importlib.util


class SpeechToText:
    def __init__(self) -> None:
        self.available = importlib.util.find_spec("faster_whisper") is not None

    def transcribe(self, audio_path: str) -> dict[str, object]:
        if not self.available:
            return {
                "status": "not_configured",
                "message": "faster-whisper is not installed/configured yet.",
                "text": "",
            }
        return {
            "status": "not_implemented",
            "message": "faster-whisper detected; transcription pipeline to be added.",
            "text": "",
            "audio_path": audio_path,
        }
