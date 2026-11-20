"""Add, list or remove the people who may use the pilot server. Each person gets their own secret token, shown ONCE.
  python scripts/pilot_users.py add "Volunteer A"     # prints the person's id and token (give it to them privately)
  python scripts/pilot_users.py list                  # ids and labels only, never tokens
  python scripts/pilot_users.py revoke u2             # that person's token stops working at once
The builder's own full access is the id "owner" (the shared NIVARAN_API_TOKEN, or this computer when no tokens are set up).
People see only their own cases. Only the owner can place calls."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.users import add_user, load_users, revoke_user, users_file  # noqa: E402

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "add" and len(sys.argv) > 2:
    uid, token = add_user(" ".join(sys.argv[2:]))
    print(f"added {uid}. Token (shown once, give it to this person privately):\n{token}")
elif cmd == "list":
    for u in load_users():
        print(u["id"], "-", u["label"])
    print(f"({len(load_users())} people in {users_file()})")
elif cmd == "revoke" and len(sys.argv) > 2:
    print("revoked" if revoke_user(sys.argv[2]) else "no such id")
else:
    print(__doc__)
