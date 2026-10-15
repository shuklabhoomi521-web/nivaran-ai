# Nivaran

Nivaran (Hindi: "solution") is one app that handles customer care for you. Tell it the problem once, in your language. It contacts the company and keeps going until the problem is solved.

Status: Phase 0 (setup). See `docs/PLAN.md` for the full roadmap.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env        # fill in keys as phases need them
cd backend
uvicorn app.main:app --reload   # http://127.0.0.1:8000/health
```

## Test
```bash
cd backend
python -m pytest                 # free tests only
python -m pytest -m live_api     # tests that call the real LLM (only when you choose)
```

Secrets live in `.env` (git-ignored). Never commit them.

## Phase 1: try the brain
Needs `GEMINI_API_KEY` in `.env` (free key from https://aistudio.google.com/apikey). Claude is optional: `LLM_PROVIDER=anthropic`. Then open http://127.0.0.1:8000/chat
Endpoints: `POST /cases/understand`, `POST /cases/plan`.
Real baseline run (30 problems, slows itself to the free limits): `cd backend && python -m pytest -m live_api -s`
