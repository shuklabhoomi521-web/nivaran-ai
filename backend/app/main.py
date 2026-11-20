from pathlib import Path

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.cases import router as cases_router
from app.api.letters import router as letters_router
from app.api.replies import router as replies_router
from app.api.tracked import router as tracked_router

app = FastAPI(title="Nivaran")
# Only the web preview of the app (a browser page) needs this; the phone app does not. Origins are listed, never "*".
app.add_middleware(CORSMiddleware, allow_origins=[o for o in os.getenv("CORS_ORIGINS", "http://localhost:8081,http://127.0.0.1:8081").split(",") if o],
                   allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type"])
app.include_router(cases_router)
app.include_router(tracked_router)
app.include_router(letters_router)
app.include_router(replies_router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/chat", include_in_schema=False)
def chat_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "chat.html")
