"""Start / stop everything for a test phone call, and place the call.

  python scripts/phone_session.py start    # tunnel + voice server in REAL mode (Sarvam hears the call). Places NO call.
  python scripts/phone_session.py status   # what is running
  python scripts/phone_session.py call     # place the test call (needs `start` first; rings the allowed number from .env)
  python scripts/phone_session.py stop     # close the tunnel and the server

Safety: the call only goes to the number in PHONE_ALLOWED_NUMBERS (one number), the AI says it is an AI first, and you can hang up from
http://localhost:7861/phone/control at any time. The tunnel exists only between `start` and `stop`."""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".phone_session.json"
load_dotenv(ROOT / ".env")
PORT = int(os.getenv("VOICE_PORT", "7861"))
LOCAL = f"http://localhost:{PORT}"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def start() -> None:
    if _state() and any(_alive(p) for p in (_state().get("tunnel_pid", 0), _state().get("server_pid", 0))):
        print("Already running. Use `status`, or `stop` first.")
        return
    subprocess.run(["pkill", "-f", "app.voice.server"], check=False)
    time.sleep(1)
    tun_log = open("/tmp/nivaran_tunnel.log", "w")
    tunnel = subprocess.Popen(["cloudflared", "tunnel", "--no-autoupdate", "--url", LOCAL], stdout=tun_log, stderr=subprocess.STDOUT, start_new_session=True)
    url = None
    for _ in range(60):
        time.sleep(1)
        text = Path("/tmp/nivaran_tunnel.log").read_text()
        if "failed to request quick Tunnel" in text:
            tunnel.terminate()
            sys.exit("Cloudflare's tunnel service is not reachable from this network (connection reset). Try another network, for example your phone's hotspot.")
        m = re.search(r"https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com", text)
        if m:
            url = m.group(0)
            break
    if not url:
        tunnel.terminate()
        sys.exit("The tunnel did not start. See /tmp/nivaran_tunnel.log")
    env = {**os.environ, "PUBLIC_BASE_URL": url, "STT_PROVIDER": "sarvam", "STT_FALLBACK": "local", "PHONE_REHEARSAL": ""}
    env.pop("PHONE_REHEARSAL")
    srv_log = open("/tmp/nivaran_server.log", "w")
    server = subprocess.Popen([sys.executable, "-m", "app.voice.server"], cwd=ROOT / "backend", env=env, stdout=srv_log, stderr=subprocess.STDOUT, start_new_session=True)
    STATE.write_text(json.dumps({"tunnel_pid": tunnel.pid, "server_pid": server.pid, "url": url, "started": time.strftime("%H:%M:%S")}))
    for _ in range(90):
        time.sleep(2)
        try:
            if httpx.get(f"{LOCAL}/voice/ready", timeout=3).json().get("ready"):
                break
        except Exception:  # noqa: BLE001
            pass
    else:
        sys.exit("The voice server did not become ready. See /tmp/nivaran_server.log")
    status()
    print("\nReady. NO call has been placed. When you say go, run:  python scripts/phone_session.py call")


def status() -> None:
    s = _state()
    if not s:
        print("Nothing running.")
        return
    print(f"tunnel: {'running' if _alive(s['tunnel_pid']) else 'STOPPED'}   server: {'running' if _alive(s['server_pid']) else 'STOPPED'}   since {s['started']}")
    print(f"public address: {s['url']}")
    try:
        ok = httpx.get(f"{s['url']}/voice/ready", timeout=15).json()
        print(f"reachable from the internet: yes ({ok})")
    except Exception as e:  # noqa: BLE001
        print(f"reachable from the internet: NO ({type(e).__name__})")
    print(f"call control + live transcript: {LOCAL}/phone/control")


def call() -> None:
    s = _state()
    if not s or not _alive(s["server_pid"]) or not _alive(s["tunnel_pid"]):
        sys.exit("Run `start` first (the tunnel and server are not both running).")
    numbers = [n for n in os.getenv("PHONE_ALLOWED_NUMBERS", "").split(",") if n.strip()]
    if len(numbers) != 1:
        sys.exit("PHONE_ALLOWED_NUMBERS must hold exactly one number for this test.")
    case = {"company": "Swiggy", "problem_summary": "The order arrived cold and no refund was given.", "user_goal": "refund",
            "details_known": [{"name": "order_id", "value": "4839201"}]}
    r = httpx.post(f"{LOCAL}/phone/call", json={"to_number": numbers[0], "case": case, "language": "en-IN", "confirm": True}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"The call was NOT placed: {r.status_code} {r.text[:300]}")
    print("Calling now. Answer the phone, press any key if Twilio plays its trial message, and play the customer-care agent.")
    print(f"Live transcript and the Hang up button: {LOCAL}/phone/control")


def stop() -> None:
    s = _state()
    for key in ("tunnel_pid", "server_pid"):
        pid = s.get(key)
        if pid and _alive(pid):
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except OSError:
                pass
    subprocess.run(["pkill", "-f", "app.voice.server"], check=False)
    subprocess.run(["pkill", "-f", "cloudflared tunnel"], check=False)
    STATE.unlink(missing_ok=True)
    print("Tunnel and server stopped.")


if __name__ == "__main__":
    {"start": start, "status": status, "call": call, "stop": stop}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
