from app.config import ConfigError, get_settings
from app.speech.base import SpeechToText, TextToSpeech


def make_stt() -> SpeechToText:
    p = get_settings().stt_provider
    if p == "gemini":
        from app.speech.gemini import GeminiSTT
        return GeminiSTT()
    raise ConfigError(f"Unknown STT_PROVIDER {p!r}. Available: gemini.")


def make_tts() -> TextToSpeech:
    p = get_settings().tts_provider
    if p == "gemini":
        from app.speech.gemini import GeminiTTS
        return GeminiTTS()
    raise ConfigError(f"Unknown TTS_PROVIDER {p!r}. Available: gemini.")
