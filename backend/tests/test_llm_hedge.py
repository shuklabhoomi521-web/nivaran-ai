import time
from types import SimpleNamespace

import pytest

from app.brain.llm import GeminiLLM


def make(slow_main=1.0, backup_delay=0.0, fail_main=False, hedge=0.2):
    llm = GeminiLLM.__new__(GeminiLLM)
    llm._settings = SimpleNamespace(gemini_model="main", gemini_backup_model="backup", gemini_hedge_seconds=hedge)
    calls = []

    def generate_content(model, contents, config):
        calls.append(model)
        if model == "main":
            time.sleep(slow_main)
            if fail_main:
                raise RuntimeError("main down")
            return SimpleNamespace(text='{"from": "main"}')
        time.sleep(backup_delay)
        return SimpleNamespace(text='{"from": "backup"}')

    llm._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    return llm, calls


def test_fast_main_model_is_used_and_the_backup_is_never_asked():
    llm, calls = make(slow_main=0.0)
    assert llm._ask("hi", None).text == '{"from": "main"}' and calls == ["main"]


def test_slow_main_model_is_beaten_by_the_backup():
    llm, calls = make(slow_main=2.0, backup_delay=0.0)
    t = time.time()
    r = llm._ask("hi", None)
    assert r.text == '{"from": "backup"}' and time.time() - t < 1.0 and calls == ["main", "backup"]


def test_if_the_main_model_fails_the_backup_still_answers():
    llm, _ = make(slow_main=0.0, fail_main=True)
    assert llm._ask("hi", None).text == '{"from": "backup"}'


def test_backup_can_be_turned_off():
    llm, calls = make(slow_main=0.3)
    llm._settings.gemini_backup_model = "none"
    assert llm._ask("hi", None).text == '{"from": "main"}' and calls == ["main"]
