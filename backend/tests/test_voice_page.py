from pathlib import Path

PAGE = (Path(__file__).resolve().parents[1] / "static" / "voice_test.html").read_text(encoding="utf-8")


def test_a_new_session_does_not_replay_the_events_of_old_sessions():
    # the page must start reading events after the newest old one, not from zero (that showed 'connected' and the greeting twice)
    start = PAGE.index("async function start()")
    assert "since = 0;" not in PAGE[start:start + 400].split("try {")[0]
    assert 'fetch("/voice/events?since=0")' in PAGE[start:start + 700]


def test_the_server_start_line_is_the_last_thing_in_server_py():
    # when run as `python -m app.voice.server`, routes defined AFTER the start line would silently not exist (phone routes were missing once)
    src = (Path(__file__).resolve().parents[1] / "app" / "voice" / "server.py").read_text(encoding="utf-8")
    assert src.count("@app.") > 0 and "@app." not in src[src.index('if __name__ == "__main__":'):]
