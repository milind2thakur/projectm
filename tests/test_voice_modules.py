from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech


def test_stt_not_configured_returns_clear_message(monkeypatch) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _name: None)
    stt = SpeechToText()
    result = stt.transcribe_from_microphone()
    assert result["status"] == "not_configured"
    assert "Install faster-whisper" in result["message"]


def test_tts_noop_when_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _name: None)
    tts = TextToSpeech()
    result = tts.speak("hello")
    assert result["status"] == "noop"
