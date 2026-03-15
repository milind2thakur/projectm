"""Speech-to-text helpers powered by faster-whisper with mic capture."""

from __future__ import annotations

import importlib
import importlib.util
import tempfile
import wave
from pathlib import Path
from typing import Any


class SpeechToText:
    """Speech-to-text wrapper with graceful fallback when deps are missing."""

    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name
        self._fw_available = importlib.util.find_spec("faster_whisper") is not None
        self._sd_available = importlib.util.find_spec("sounddevice") is not None
        self._np_available = importlib.util.find_spec("numpy") is not None
        self.available = self._fw_available and self._sd_available and self._np_available
        self._model: Any | None = None

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        fw_module = importlib.import_module("faster_whisper")
        self._model = fw_module.WhisperModel(self.model_name, device="auto", compute_type="int8")
        return self._model

    def transcribe(self, audio_path: str) -> dict[str, object]:
        if not self._fw_available:
            return {
                "status": "not_configured",
                "message": "faster-whisper is not installed/configured yet.",
                "text": "",
            }
        try:
            model = self._get_model()
            segments, _ = model.transcribe(audio_path, beam_size=1, vad_filter=True)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            if not text:
                return {"status": "empty", "message": "No speech detected.", "text": ""}
            return {"status": "success", "message": "Transcription complete.", "text": text, "audio_path": audio_path}
        except Exception as exc:
            return {"status": "error", "message": f"Transcription failed: {exc}", "text": "", "audio_path": audio_path}

    def transcribe_from_microphone(self, seconds: int = 4, sample_rate: int = 16000) -> dict[str, object]:
        if not self.available:
            return {
                "status": "not_configured",
                "message": "Install faster-whisper, sounddevice, and numpy for voice input.",
                "text": "",
            }

        try:
            sd = importlib.import_module("sounddevice")
            np = importlib.import_module("numpy")

            frames = int(seconds * sample_rate)
            recording = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = Path(tmp.name)

            with wave.open(str(audio_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(np.asarray(recording).tobytes())

            result = self.transcribe(str(audio_path))
            result["audio_path"] = str(audio_path)
            return result
        except Exception as exc:
            return {"status": "error", "message": f"Microphone capture failed: {exc}", "text": ""}
