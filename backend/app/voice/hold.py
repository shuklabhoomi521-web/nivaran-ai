"""Hold-music detection. While we wait on a phone line, the other side plays music (or a repeating message) and nobody speaks.
Rule: for HOLD_AFTER seconds of audio there was clearly sound (not silence) but the voice detector found almost no speech -> we are on hold.
Speech coming back ends the hold. While on hold the AI waits quietly (it does not answer the music)."""
import numpy as np
from pipecat.frames.frames import Frame, InputAudioRawFrame, VADUserStartedSpeakingFrame, VADUserStoppedSpeakingFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

SOUND_RMS = 400            # 16-bit audio: above this a frame counts as "sound" (a quiet line is far below)
HOLD_AFTER = 8.0           # seconds of sound without speech before we say "on hold"
WINDOW = 10.0              # we look at the last 10 seconds


class HoldDetector:
    """Pure logic (no pipecat), easy to test: feed it audio and 'is speech' signals, it keeps `on_hold`."""

    def __init__(self) -> None:
        self.on_hold = False
        self._frames: list[tuple[float, bool, bool]] = []     # (seconds, has_sound, speech_active)
        self._speaking = False
        self._clock = 0.0

    def speech(self, active: bool) -> None:
        self._speaking = active
        if active:                                            # a person started talking: the hold is over
            self.on_hold = False
            self._frames.clear()

    def audio(self, pcm: bytes, sample_rate: int) -> bool:
        """Returns True when the hold state changed."""
        x = np.frombuffer(pcm, dtype="<i2").astype(np.float64)
        if not len(x):
            return False
        secs = len(x) / sample_rate
        self._clock += secs
        self._frames.append((secs, float(np.sqrt(np.mean(x ** 2))) > SOUND_RMS, self._speaking))
        while sum(f[0] for f in self._frames) > WINDOW:
            self._frames.pop(0)
        total = sum(f[0] for f in self._frames)
        if total < HOLD_AFTER or self.on_hold:
            return False
        sound = sum(f[0] for f in self._frames if f[1]) / total
        spoken = sum(f[0] for f in self._frames if f[2]) / total
        if sound > 0.7 and spoken < 0.1:
            self.on_hold = True
            return True
        return False


class HoldProcessor(FrameProcessor):
    def __init__(self, on_change=None, **kwargs):
        super().__init__(**kwargs)
        self.detector, self._on_change = HoldDetector(), on_change

    @property
    def on_hold(self) -> bool:
        return self.detector.on_hold

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        before = self.detector.on_hold
        if isinstance(frame, VADUserStartedSpeakingFrame):
            self.detector.speech(True)
        elif isinstance(frame, VADUserStoppedSpeakingFrame):
            self.detector.speech(False)
        elif isinstance(frame, InputAudioRawFrame):
            self.detector.audio(frame.audio, frame.sample_rate)
        if self._on_change and self.detector.on_hold != before:
            self._on_change(self.detector.on_hold)
        await self.push_frame(frame, direction)
