from app.config import ConfigError, get_settings
from app.speech.base import SpeechToText, TextToSpeech

STT_NAMES = ("sarvam", "gemini", "gemini_prompt", "groq")
TTS_NAMES = ("sarvam", "gemini")


def _check(name: str, allowed: tuple, what: str) -> None:
    if name not in allowed:
        raise ConfigError(f"Unknown {what} {name!r}. Available: {', '.join(allowed)}.")


def _stt(name: str) -> SpeechToText:
    _check(name, STT_NAMES, "STT_PROVIDER")
    if name == "sarvam":
        from app.speech.sarvam import SarvamSTT
        return SarvamSTT()
    if name == "groq":
        from app.speech.groq import GroqSTT
        return GroqSTT()
    if name == "gemini_prompt":
        from app.speech.gemini import GeminiPromptSTT
        return GeminiPromptSTT()
    from app.speech.gemini import GeminiSTT
    return GeminiSTT()


def _tts(name: str) -> TextToSpeech:
    _check(name, TTS_NAMES, "TTS_PROVIDER")
    if name == "sarvam":
        from app.speech.sarvam import SarvamTTS
        return SarvamTTS()
    from app.speech.gemini import GeminiTTS
    return GeminiTTS()


def _ledger(primary: str):
    if primary == "sarvam":
        from app.speech.credits import CreditLedger
        return CreditLedger()
    return None


def make_stt(fallback: bool = True) -> SpeechToText:
    """Default: Sarvam, with Gemini as the backup. fallback=False gives the plain provider (the bake-off uses this)."""
    s = get_settings()
    _check(s.stt_provider, STT_NAMES, "STT_PROVIDER")
    if not fallback or s.stt_fallback in ("none", s.stt_provider):
        return _stt(s.stt_provider)
    _check(s.stt_fallback, STT_NAMES, "STT_FALLBACK")
    from app.speech.fallback import FallbackSTT
    return FallbackSTT(lambda: _stt(s.stt_provider), lambda: _stt(s.stt_fallback), "speech-to-text", _ledger(s.stt_provider))


def make_tts(fallback: bool = True) -> TextToSpeech:
    s = get_settings()
    if s.tts_by_language and fallback:
        for name in s.tts_by_language.values():
            _check(name, TTS_NAMES, "TTS_BY_LANGUAGE")
        return RoutedTTS(s.tts_by_language, s.tts_provider)
    _check(s.tts_provider, TTS_NAMES, "TTS_PROVIDER")
    if not fallback or s.tts_fallback in ("none", s.tts_provider):
        return _tts(s.tts_provider)
    _check(s.tts_fallback, TTS_NAMES, "TTS_FALLBACK")
    from app.speech.fallback import FallbackTTS
    return FallbackTTS(lambda: _tts(s.tts_provider), lambda: _tts(s.tts_fallback), "text-to-speech", _ledger(s.tts_provider))


class RoutedTTS:
    """The founder's voice picks: each language has its own voice provider; if that one fails, the other speaks instead."""

    def __init__(self, picks: dict, default: str) -> None:
        self.picks, self.default = picks, default
        self._cache: dict = {}
        self.fallbacks_used = 0
        self._skip_until: dict = {}        # a voice that just failed is not tried again for a while

    def _provider(self, name: str):
        if name not in self._cache:
            if name == "gemini":
                from app.speech.gemini import GeminiTTS
                self._cache[name] = GeminiTTS(hard_timeout=5)       # a free voice that hangs must not hold a live chat
            else:
                self._cache[name] = _tts(name)
        return self._cache[name]

    def synthesize(self, text: str, language: str | None = None, voice: str | None = None):
        import time
        first = self.picks.get(language, self.default)
        other = "sarvam" if first == "gemini" else "gemini"
        if self._skip_until.get(first, 0) > time.time():      # it failed a moment ago: go straight to the other voice
            first, other = other, first
        try:
            return self._provider(first).synthesize(text, language)
        except Exception:  # noqa: BLE001 - any failure of the picked voice: use the other one
            self.fallbacks_used += 1
            self._skip_until[first] = time.time() + 300
            return self._provider(other).synthesize(text, language)
