"""Sarvam first, Gemini as the backup: if Sarvam fails, is missing its key, or its credit is used up, the backup answers
and the answer says which provider really spoke."""
import logging
from typing import Callable

from app.brain.ratelimit import DailyQuotaExceeded
from app.config import ConfigError
from app.speech.base import SpeechAudio, SpeechError, Transcript

log = logging.getLogger("nivaran.speech")


class _Fallback:
    def __init__(self, primary_factory: Callable, backup_factory: Callable | None, name: str, ledger=None) -> None:
        self._name, self._ledger = name, ledger
        self._backup_factory, self._backup = backup_factory, None
        self.primary = None
        self.primary_problem: str | None = None
        try:
            self.primary = primary_factory()
        except ConfigError as e:           # for example no Sarvam key: run on the backup only
            self.primary_problem = str(e)
            log.warning("%s: primary not available (%s). Using the backup.", name, e)
        self.fallbacks_used = 0

    def _backup_provider(self):
        if self._backup is None:
            if self._backup_factory is None:
                raise SpeechError(f"{self._name}: primary failed and no backup is configured.")
            self._backup = self._backup_factory()
        return self._backup

    def _run(self, call_primary: Callable, call_backup: Callable):
        why = self.primary_problem
        if self.primary is not None:
            if self._ledger is not None and self._ledger.blocked():
                why = "Sarvam credit is below the line (needs the founder's yes) or used up"
            else:
                try:
                    return call_primary(self.primary)
                except (SpeechError, DailyQuotaExceeded) as e:
                    why = f"primary failed: {str(e)[:120]}"
        self.fallbacks_used += 1
        log.warning("%s: using the backup (%s)", self._name, why)
        return call_backup(self._backup_provider())


class FallbackSTT(_Fallback):
    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        t = self._run(lambda p: p.transcribe(audio, mime_type, language), lambda p: p.transcribe(audio, mime_type, language))
        if t.provider is None:
            t.provider = "backup" if self.fallbacks_used else "primary"
        return t


class FallbackTTS(_Fallback):
    def synthesize(self, text: str, language: str | None = None, voice: str | None = None) -> SpeechAudio:
        a = self._run(lambda p: p.synthesize(text, language), lambda p: p.synthesize(text, language, voice))
        if a.provider is None:
            a.provider = "backup" if self.fallbacks_used else "primary"
        return a
