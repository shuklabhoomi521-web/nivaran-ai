"""A free speech-to-text model that runs on this laptop (no internet at call time, no credit).
Whisper-Hindi2Hinglish-Apex: Hindi and English speech written as Hinglish in English letters. Hindi and English only (no Tamil)."""
import io
import threading
import wave

import numpy as np

from app.config import get_settings
from app.speech.base import SpeechError, Transcript

_cache: dict = {}
_lock = threading.Lock()      # one transcription at a time: two at once make both several times slower


class LocalWhisperSTT:
    def __init__(self) -> None:
        self._model_id = get_settings().local_stt_model

    def _pipe(self):
        if "pipe" not in _cache:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            dtype = torch.float32     # float16 on the Mac GPU gave empty garbage ("0!"), so use full precision
            model = AutoModelForSpeechSeq2Seq.from_pretrained(self._model_id, torch_dtype=dtype, low_cpu_mem_usage=True, use_safetensors=True)
            model.to(device)
            proc = AutoProcessor.from_pretrained(self._model_id)
            _cache["pipe"] = pipeline("automatic-speech-recognition", model=model, tokenizer=proc.tokenizer,
                                      feature_extractor=proc.feature_extractor, torch_dtype=dtype, device=device,
                                      generate_kwargs={"task": "transcribe", "language": "en"})     # "en" = write in English letters (the model's own recommended setting)
        return _cache["pipe"]

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        try:
            with wave.open(io.BytesIO(audio), "rb") as w:
                rate, pcm = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
            x = pcm.astype(np.float32) / 32768
            if rate != 16000:
                x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * 16000 / rate)), np.arange(len(x)), x).astype(np.float32)
            with _lock:
                text = self._pipe()({"raw": x, "sampling_rate": 16000})["text"].strip()
        except Exception as e:  # noqa: BLE001
            raise SpeechError(f"Local speech model failed: {type(e).__name__}: {str(e)[:100]}") from e
        return Transcript(text=text, language=language, provider="local")
