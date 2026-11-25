from pathlib import Path

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.calls import router as calls_router
from app.api.cases import router as cases_router
from app.auth import access_guard
from app.api.letters import router as letters_router
from app.api.replies import router as replies_router
from app.api.profile import router as profile_router
from app.api.speech import router as speech_router
from app.api.tracked import router as tracked_router

app = FastAPI(title="Nivaran")
# Only the web preview of the app (a browser page) needs this; the phone app does not. Origins are listed, never "*".
app.add_middleware(BaseHTTPMiddleware, dispatch=access_guard)
app.add_middleware(CORSMiddleware, allow_origins=[o for o in os.getenv("CORS_ORIGINS", "http://localhost:8081,http://127.0.0.1:8081").split(",") if o],
                   allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Content-Type", "Authorization"])
app.include_router(cases_router)
app.include_router(tracked_router)
app.include_router(letters_router)
app.include_router(replies_router)
app.include_router(speech_router)
app.include_router(calls_router)
app.include_router(profile_router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
WEB_DIST = Path(os.getenv("WEB_DIST", str(Path(__file__).resolve().parents[2] / "mobile" / "dist")))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/chat", include_in_schema=False)
def chat_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "chat.html")


if (WEB_DIST / "index.html").exists():          # one link for everything: the web build of the app, built with `npm run build:web` in mobile/
    app.mount("/app", StaticFiles(directory=WEB_DIST, html=True), name="web-app")
