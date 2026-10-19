from app.config import ConfigError, get_settings
from app.speech.base import SpeechToText, TextToSpeech


def make_stt() -> SpeechToText:
    p = get_settings().stt_provider
    if p == "gemini":
        from app.speech.gemini import GeminiSTT
        return GeminiSTT()
    if p == "gemini_prompt":
        from app.speech.gemini import GeminiPromptSTT
        return GeminiPromptSTT()
    raise ConfigError(f"Unknown STT_PROVIDER {p!r}. Available: gemini, gemini_prompt.")


def make_tts() -> TextToSpeech:
    p = get_settings().tts_provider
    if p == "gemini":
        from app.speech.gemini import GeminiTTS
        return GeminiTTS()
    raise ConfigError(f"Unknown TTS_PROVIDER {p!r}. Available: gemini.")
