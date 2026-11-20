"""Access control for the backend. The case files hold private details, so the API must not be open, and one person must never see another's.
Who is calling is decided here and put on the request (`request.state.user_id`):
1. A personal token from `.pilot_users.json` (see `app/users.py`) means that person.
2. The shared `NIVARAN_API_TOKEN`, if set, means the builder ("owner").
3. If neither kind of token is set up: only this computer is accepted, as "owner".
Anything else gets 401. /health is open. Browser pre-flight checks (OPTIONS) are let through so the web preview can ask first."""
import hmac
import os

from fastapi import Request
from fastapi.responses import JSONResponse

from app.users import LEGACY_OWNER, find_user, load_users

OPEN_PATHS = {"/health"}
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


def current_user(request: Request) -> str:
    return getattr(request.state, "user_id", LEGACY_OWNER)


def is_owner(user: str) -> bool:
    return user == LEGACY_OWNER


async def access_guard(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in OPEN_PATHS:
        return await call_next(request)
    shared = os.getenv("NIVARAN_API_TOKEN", "").strip()
    users = load_users()
    given = request.headers.get("authorization", "")
    token = given[7:].strip() if given.startswith("Bearer ") else ""
    user = None
    if token:
        user = find_user(token)
        if user is None and shared and hmac.compare_digest(token.encode(), shared.encode()):
            user = LEGACY_OWNER
    if user is None:
        if shared or users:
            return JSONResponse({"detail": "missing or wrong access token"}, status_code=401)
        host = request.client.host if request.client else ""
        if host not in LOCAL_HOSTS:
            return JSONResponse({"detail": "this server only answers the computer it runs on until NIVARAN_API_TOKEN is set or people are added"}, status_code=401)
        user = LEGACY_OWNER
    request.state.user_id = user
    return await call_next(request)
