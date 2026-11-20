"""Access control for the backend. The case files hold private details, so the API must not be open to a whole Wi-Fi network.
- If NIVARAN_API_TOKEN is set: every route except /health needs the header  Authorization: Bearer <token>.
- If it is not set: only requests from this computer (127.0.0.1 or ::1) are accepted; everyone else gets 401.
Browser pre-flight checks (OPTIONS) are let through so the web preview can ask first."""
import hmac
import os

from fastapi import Request
from fastapi.responses import JSONResponse

OPEN_PATHS = {"/health"}
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


async def access_guard(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in OPEN_PATHS:
        return await call_next(request)
    token = os.getenv("NIVARAN_API_TOKEN", "").strip()
    if token:
        given = request.headers.get("authorization", "")
        if not (given.startswith("Bearer ") and hmac.compare_digest(given[7:].strip().encode(), token.encode())):
            return JSONResponse({"detail": "missing or wrong access token"}, status_code=401)
    else:
        host = request.client.host if request.client else ""
        if host not in LOCAL_HOSTS:
            return JSONResponse({"detail": "this server only answers the computer it runs on until NIVARAN_API_TOKEN is set"}, status_code=401)
    return await call_next(request)
