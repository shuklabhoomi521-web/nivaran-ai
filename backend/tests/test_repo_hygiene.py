import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = (".aac", ".wav", ".m4a", ".mp3", ".aiff", ".caf", ".ogg", ".flac", ".zip", ".tar.gz", ".parquet")


def test_no_voice_recordings_or_big_downloads_are_tracked_by_git():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    bad = [f for f in files if f.lower().endswith(FORBIDDEN)]
    assert not bad, f"Audio or archive files must never be committed (people's voices, big downloads): {bad}"


def test_secrets_files_are_not_tracked():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    assert ".env" not in files and not [f for f in files if f.endswith((".sarvam_credits.json", ".llm_usage.json", ".speech_usage.json"))]
