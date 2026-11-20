import base64
import binascii

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.safety.redact import redact
from app.speech.base import SpeechError, SpeechToText
from app.speech.factory import make_stt

router = APIRouter(prefix="/speech", tags=["speech"])

MAX_AUDIO_BYTES = 3_000_000          # about a minute of phone-quality speech; longer recordings are refused
ALLOWED_TYPES = ("audio/wav", "audio/x-wav", "audio/mp4", "audio/m4a", "audio/x-m4a", "audio/aac", "audio/mpeg", "audio/webm", "audio/ogg")


def get_stt() -> SpeechToText:
    return make_stt()


class TranscribeRequest(BaseModel):
    audio_b64: str
    mime_type: str
    language: str | None = None      # a hint such as "hi-IN"; None lets the speech service detect it


class TranscribeResponse(BaseModel):
    text: str
    language: str | None
    provider: str | None
    redacted: list[str]              # kinds of payment data removed from what was heard


@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe(req: TranscribeRequest, stt: SpeechToText = Depends(get_stt)):
    """Turn a short recording into text for the new-case box. The text is cleaned of card, CVV and PIN (strict mode, because speech
    often spells digits out) before it is returned. The audio itself is never stored."""
    if req.mime_type.split(";")[0].strip().lower() not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"unsupported audio type {req.mime_type}")
    try:
        audio = base64.b64decode(req.audio_b64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=422, detail="the audio is not valid base64")
    if not audio:
        raise HTTPException(status_code=422, detail="the recording is empty")
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="the recording is too long: keep it under about a minute")
    try:
        t = stt.transcribe(audio, req.mime_type.split(";")[0].strip().lower(), req.language)
    except SpeechError as e:
        raise HTTPException(status_code=502, detail=str(e))
    clean, kinds = redact(t.text or "", strict=True)
    if not clean.strip():
        raise HTTPException(status_code=422, detail="nothing was heard: try again closer to the microphone")
    return TranscribeResponse(text=clean.strip(), language=t.language, provider=t.provider, redacted=kinds)
