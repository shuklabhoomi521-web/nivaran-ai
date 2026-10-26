"""Make browser audio sound like a phone line: only the narrow telephone band (about 300 to 3400 Hz), squeezed by the mu-law phone coding.
Used by the browser fallback for phone calls, so the speech-to-text hears what it would hear on a real call."""
import audioop

import numpy as np

from pipecat.frames.frames import Frame, InputAudioRawFrame, OutputAudioRawFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class LineDegrader:
    """Keeps a little state between chunks so there are no clicks at the joins."""

    TAPS = 101

    def __init__(self) -> None:
        self._down = self._up = None
        self._tail = np.zeros(self.TAPS - 1)
        self._fir: dict[int, np.ndarray] = {}

    def _lowpass(self, pcm: bytes, rate: int) -> bytes:
        """Cut everything above 3.4 kHz BEFORE going down to 8 kHz (otherwise high sounds fold back into the speech band)."""
        if rate not in self._fir:
            n = np.arange(self.TAPS) - (self.TAPS - 1) / 2
            h = np.sinc(2 * 3400 / rate * n) * np.hamming(self.TAPS)
            self._fir[rate] = h / h.sum()
        x = np.concatenate([self._tail, np.frombuffer(pcm, "<i2").astype(float)])
        self._tail = x[-(self.TAPS - 1):]
        y = np.convolve(x, self._fir[rate], mode="valid")[: len(x) - (self.TAPS - 1)]
        return np.clip(y, -32768, 32767).astype("<i2").tobytes()

    def process(self, pcm: bytes, rate: int) -> bytes:
        if not pcm or rate == 8000:
            return audioop.ulaw2lin(audioop.lin2ulaw(pcm, 2), 2) if pcm else pcm
        pcm = self._lowpass(pcm, rate)
        low, self._down = audioop.ratecv(pcm, 2, 1, rate, 8000, self._down)        # down to the phone's 8 kHz (drops everything above 4 kHz)
        low = audioop.ulaw2lin(audioop.lin2ulaw(low, 2), 2)                        # the phone company's mu-law squeeze
        back, self._up = audioop.ratecv(low, 2, 1, 8000, rate, self._up)           # back up so the rest of the pipeline is unchanged
        return back


class PhoneLine(FrameProcessor):
    """Put it twice in the pipeline: after the transport's input (what the agent says) and before its output (what the AI says)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._in, self._out = LineDegrader(), LineDegrader()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, InputAudioRawFrame) and frame.num_channels == 1:
            frame.audio = self._in.process(frame.audio, frame.sample_rate)
        elif isinstance(frame, OutputAudioRawFrame) and frame.num_channels == 1:
            frame.audio = self._out.process(frame.audio, frame.sample_rate)
        await self.push_frame(frame, direction)
