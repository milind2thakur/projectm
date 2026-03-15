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


def test_stt_retries_until_success(monkeypatch) -> None:
    stt = SpeechToText()
    stt.available = True
    monkeypatch.setattr(stt, "_capture_to_wav", lambda _seconds, _rate: "dummy.wav")
    states = iter(
        [
            {"status": "empty", "message": "No speech detected.", "text": ""},
            {"status": "success", "message": "ok", "text": "open firefox", "audio_path": "dummy.wav"},
        ]
    )
    monkeypatch.setattr(stt, "transcribe", lambda _audio_path: next(states))
    result = stt.transcribe_from_microphone(retries=2)
    assert result["status"] == "success"
    assert result["text"] == "open firefox"
    assert result["attempt"] == 2


def test_stt_short_text_filtered_as_noisy(monkeypatch) -> None:
    stt = SpeechToText(min_text_chars=6)
    stt.available = True
    monkeypatch.setattr(stt, "_capture_to_wav", lambda _seconds, _rate: "dummy.wav")
    monkeypatch.setattr(
        stt,
        "transcribe",
        lambda _audio_path: {"status": "success", "message": "ok", "text": "ok", "audio_path": "dummy.wav"},
    )
    result = stt.transcribe_from_microphone(retries=1)
    assert result["status"] == "empty"
    assert "too short/noisy" in result["message"]
