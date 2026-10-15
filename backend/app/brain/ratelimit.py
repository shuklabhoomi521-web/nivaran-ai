"""Keeps us inside the free limits by slowing down.

RPM = requests per minute: we wait between calls so we never go faster than that.
RPD = requests per day: we count calls in a small file and stop before the cap.
Google resets daily limits at midnight Pacific time, so we count days in that time zone.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

USAGE_FILE = Path(__file__).resolve().parents[3] / ".llm_usage.json"  # git-ignored
PACIFIC = ZoneInfo("America/Los_Angeles")


class DailyQuotaExceeded(RuntimeError):
    pass


class RateLimiter:
    def __init__(self, rpm: int, rpd: int = 0, *, usage_file: Path = USAGE_FILE,
                 clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep,
                 today: Callable[[], str] | None = None):
        self.min_gap = 60.0 / rpm if rpm > 0 else 0.0
        self.rpd = rpd
        self.usage_file = usage_file
        self._clock, self._sleep = clock, sleep
        self._today = today or (lambda: datetime.now(PACIFIC).date().isoformat())
        self._last: float | None = None

    def _read(self) -> dict:
        try:
            return json.loads(self.usage_file.read_text())
        except (OSError, ValueError):
            return {}

    def used_today(self) -> int:
        return int(self._read().get(self._today(), 0))

    def acquire(self) -> None:
        """Call before every request. Sleeps if needed. Raises when today's cap is used up."""
        day = self._today()
        data = self._read()
        if self.rpd and data.get(day, 0) >= self.rpd:
            raise DailyQuotaExceeded(
                f"Daily limit of {self.rpd} requests reached. Try again after midnight Pacific time.")
        if self._last is not None:
            wait = self.min_gap - (self._clock() - self._last)
            if wait > 0:
                self._sleep(wait)
        self._last = self._clock()
        try:
            self.usage_file.write_text(json.dumps({day: data.get(day, 0) + 1}))
        except OSError:
            pass  # counting is best effort; the server's own 429 is the final guard
