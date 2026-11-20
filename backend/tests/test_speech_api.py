import base64

from fastapi.testclient import TestClient

from app.api import speech as speech_api
from app.main import app
from app.speech.base import SpeechError, Transcript


class FakeSTT:
    def __init__(self, text="my swiggy order arrived cold", language="en-IN", fail=False):
        self.text, self.language, self.fail, self.calls = text, language, fail, []

    def transcribe(self, audio, mime_type, language=None):
        self.calls.append((len(audio), mime_type, language))
        if self.fail:
            raise SpeechError("the speech service did not answer")
        return Transcript(text=self.text, language=self.language, provider="fake")


def post(stt, **over):
    app.dependency_overrides[speech_api.get_stt] = lambda: stt
    try:
        body = {"audio_b64": base64.b64encode(b"RIFFfakeaudio").decode(), "mime_type": "audio/wav", "language": "en-IN", **over}
        return TestClient(app).post("/speech/transcribe", json=body)
    finally:
        app.dependency_overrides.clear()


def test_happy_path_returns_text_and_which_provider_answered():
    stt = FakeSTT()
    r = post(stt)
    assert r.status_code == 200 and r.json() == {"text": "my swiggy order arrived cold", "language": "en-IN", "provider": "fake", "redacted": []}
    assert stt.calls == [(13, "audio/wav", "en-IN")]


def test_spoken_card_numbers_and_pins_are_removed_before_the_text_leaves():
    r = post(FakeSTT(text="my card is 4111 1111 1111 1111 and my upi pin 4829 please refund"))
    j = r.json()
    assert r.status_code == 200 and "4111" not in j["text"] and "4829" not in j["text"] and set(j["redacted"]) >= {"card_number", "pin"}


def test_bad_input_is_refused_with_clear_messages():
    assert post(FakeSTT(), mime_type="text/plain").status_code == 415
    assert post(FakeSTT(), audio_b64="***not base64***").status_code == 422
    assert post(FakeSTT(), audio_b64="").status_code == 422
    big = base64.b64encode(b"x" * (speech_api.MAX_AUDIO_BYTES + 1)).decode()
    assert post(FakeSTT(), audio_b64=big).status_code == 413


def test_codec_parameters_in_the_mime_type_are_accepted_and_empty_speech_is_a_clear_error():
    stt = FakeSTT()
    assert post(stt, mime_type="audio/webm;codecs=opus").status_code == 200 and stt.calls[0][1] == "audio/webm"
    r = post(FakeSTT(text="   "))
    assert r.status_code == 422 and "nothing was heard" in r.json()["detail"]


def test_provider_failure_is_a_502_with_the_reason():
    r = post(FakeSTT(fail=True))
    assert r.status_code == 502 and "did not answer" in r.json()["detail"]
