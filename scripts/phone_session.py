"""Start / stop everything for a test phone call, and place the call.

  python scripts/phone_session.py start    # tunnel + voice server in REAL mode (Sarvam hears the call). Places NO call.
  python scripts/phone_session.py status   # what is running
  python scripts/phone_session.py call     # place the test call (add --say for a line test: the phone just speaks one sentence) (needs `start` first; rings the allowed number from .env)
  python scripts/phone_session.py stop     # close the tunnel and the server
  python scripts/phone_session.py report   # after a call: what Twilio says and what our side saw
  python scripts/phone_session.py check    # can this network carry a tunnel? (10 seconds, no call)

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
    url, tunnel = None, None
    for attempt in range(1, 9):                       # this network resets connections now and then: try again a few times
        log = Path("/tmp/nivaran_tunnel.log")
        archive = Path(f"/tmp/nivaran_tunnel_{time.strftime('%H%M%S')}_try{attempt}.log")      # every try keeps its own log (the evidence is not overwritten)
        tunnel = subprocess.Popen(["cloudflared", "tunnel", "--no-autoupdate", "--protocol", "http2", "--edge-ip-version", "4", "--url", LOCAL],
                                  stdout=open(log, "w"), stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(40):
            time.sleep(1)
            text = log.read_text()
            m = re.search(r"https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com", text)
            if m and "Registered tunnel connection" in text:
                url = m.group(0)
                break
            if "failed to request quick Tunnel" in text or "Initiating shutdown" in text:
                break
        if url:
            break
        archive.write_text(log.read_text())
        print(f"tunnel attempt {attempt} failed, trying again...", flush=True)
        try:
            os.killpg(os.getpgid(tunnel.pid), signal.SIGTERM)
        except OSError:
            pass
        time.sleep(3)
    if not url:
        sys.exit("The tunnel did not come up after 8 tries. This network is blocking it. Try another network.")
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
    say_only = "--say" in sys.argv
    s = _state()
    if not s or not _alive(s["server_pid"]) or not _alive(s["tunnel_pid"]):
        sys.exit("Run `start` first (the tunnel and server are not both running).")
    numbers = [n for n in os.getenv("PHONE_ALLOWED_NUMBERS", "").split(",") if n.strip()]
    if len(numbers) != 1:
        sys.exit("PHONE_ALLOWED_NUMBERS must hold exactly one number for this test.")
    case = {"company": "Swiggy", "problem_summary": "The order arrived cold and no refund was given.", "user_goal": "refund",
            "details_known": [{"name": "order_id", "value": "4839201"}]}
    r = httpx.post(f"{LOCAL}/phone/call", json={"to_number": numbers[0], "case": case, "language": "en-IN", "confirm": True, "say_only": say_only}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"The call was NOT placed: {r.status_code} {r.text[:300]}")
    if say_only:
        print("LINE TEST: the phone will just say one sentence (no AI). Answer, press any key if Twilio asks.")
    print("Calling now. Answer the phone, press any key if Twilio plays its trial message, and play the customer-care agent.")
    print(f"Live transcript and the Hang up button: {LOCAL}/phone/control")


def check() -> None:
    """The REAL test: can this network carry a tunnel? Opens a tunnel for up to 40 seconds and closes it again. Places no call."""
    log = Path("/tmp/nivaran_check.log")
    p = subprocess.Popen(["cloudflared", "tunnel", "--no-autoupdate", "--protocol", "http2", "--edge-ip-version", "4", "--url", LOCAL],
                         stdout=open(log, "w"), stderr=subprocess.STDOUT, start_new_session=True)
    ok, why = False, "timed out"
    for _ in range(40):
        time.sleep(1)
        text = log.read_text()
        if "Registered tunnel connection" in text:
            ok = True
            break
        if "failed to request quick Tunnel" in text:
            why = "Cloudflare's tunnel service did not answer"
            break
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    except OSError:
        pass
    print("This network CAN carry the call." if ok else f"This network can NOT carry the tunnel ({why}). Switch network and run `check` again.")


def report() -> None:
    """After a call: what Twilio says happened and what OUR side saw (so a call that ends early can be explained)."""
    import os as _os
    sid, tok = _os.getenv("TWILIO_ACCOUNT_SID", ""), _os.getenv("TWILIO_AUTH_TOKEN", "")
    c = httpx.get(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json?PageSize=1", auth=(sid, tok), timeout=20).json()["calls"][0]
    print(f"Twilio says: status={c['status']}, duration={c['duration']} s, started {c['start_time']}")
    try:
        ev = httpx.get(f"{LOCAL}/voice/events", params={"since": 0}, timeout=10).json()
        for e in ev[-25:]:
            print(f"  {e['t']}  {e['kind']:6} {e['text'][:110]}")
    except Exception as e:  # noqa: BLE001
        print("our server is not running:", type(e).__name__)
    seen = "Twilio asked our server" in json.dumps(ev if 'ev' in dir() else "")
    print("\nHow to read this: instructions requested but no 'opened the audio connection' = Twilio never connected the stream (or hung up first);\n"
          "connection opened then closed within seconds = the bot or the line closed it; no instructions at all = Twilio could not reach our tunnel.")


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
    {"start": start, "status": status, "call": call, "stop": stop, "check": check, "report": report}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
