"""Guard: no tracked file may contain an absolute local path (e.g. a home folder) - it would leak a username into a public repo.
Scripts write results with paths relative to the repo root; this test keeps it that way."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ("/Users/", "/home/jai", "C:\\Users\\")
SKIP = {"backend/tests/test_no_local_paths.py", ".github/workflows/tests.yml"}


def test_no_absolute_local_paths_in_tracked_files():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    if not files or files == [""]:
        return                                   # not a git checkout (e.g. a zip download): nothing to check
    bad = []
    for name in filter(None, files):
        if name in SKIP:
            continue
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if any(f in text for f in FORBIDDEN):
            bad.append(name)
    assert not bad, f"absolute local paths found in: {bad}"
