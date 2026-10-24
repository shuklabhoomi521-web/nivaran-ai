"""Keypad tones for phone menus ("press 1 for orders"). Phone lines carry the tones as ordinary sound, so we just play them."""
import math
import struct

LOW = {"1": 697, "2": 697, "3": 697, "4": 770, "5": 770, "6": 770, "7": 852, "8": 852, "9": 852, "*": 941, "0": 941, "#": 941}
HIGH = {"1": 1209, "2": 1336, "3": 1477, "4": 1209, "5": 1336, "6": 1477, "7": 1209, "8": 1336, "9": 1477, "*": 1209, "0": 1336, "#": 1477}


def tones(digits: str, sample_rate: int = 8000, tone_ms: int = 160, gap_ms: int = 100) -> bytes:
    """16-bit mono PCM of the given keypad digits (0-9, * and #)."""
    out = bytearray()
    n_tone, n_gap = sample_rate * tone_ms // 1000, sample_rate * gap_ms // 1000
    for d in digits:
        if d not in LOW:
            continue
        for i in range(n_tone):
            t = i / sample_rate
            v = 0.45 * (math.sin(2 * math.pi * LOW[d] * t) + math.sin(2 * math.pi * HIGH[d] * t))
            out += struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767 * 0.8))
        out += b"\0\0" * n_gap
    return bytes(out)
