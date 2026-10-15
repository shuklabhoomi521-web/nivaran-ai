import pytest

from app.brain.ratelimit import DailyQuotaExceeded, RateLimiter


class Fake:
    """A fake clock: sleeping just moves time forward."""

    def __init__(self):
        self.now = 1000.0
        self.slept: list[float] = []

    def clock(self):
        return self.now

    def sleep(self, s):
        self.slept.append(s)
        self.now += s


def make(tmp_path, rpm=5, rpd=0, day="2026-10-15"):
    f = Fake()
    lim = RateLimiter(rpm, rpd, usage_file=tmp_path / "u.json", clock=f.clock, sleep=f.sleep, today=lambda: day)
    return lim, f


def test_waits_between_calls_to_respect_rpm(tmp_path):
    lim, f = make(tmp_path, rpm=5)  # one call every 12 seconds
    lim.acquire()
    assert f.slept == []
    lim.acquire()
    assert f.slept == [pytest.approx(12.0)]
    f.now += 20  # user was slow anyway: no extra waiting
    lim.acquire()
    assert len(f.slept) == 1


def test_stops_at_daily_cap_and_remembers_across_restarts(tmp_path):
    lim, _ = make(tmp_path, rpm=0, rpd=3)
    for _ in range(3):
        lim.acquire()
    assert lim.used_today() == 3
    lim2, _ = make(tmp_path, rpm=0, rpd=3)  # a fresh process reads the file
    with pytest.raises(DailyQuotaExceeded):
        lim2.acquire()


def test_new_day_resets_the_count(tmp_path):
    lim, _ = make(tmp_path, rpm=0, rpd=1, day="2026-10-15")
    lim.acquire()
    lim_next, _ = make(tmp_path, rpm=0, rpd=1, day="2026-10-16")
    lim_next.acquire()  # does not raise


def test_no_cap_when_rpd_is_zero(tmp_path):
    lim, _ = make(tmp_path, rpm=0, rpd=0)
    for _ in range(50):
        lim.acquire()
