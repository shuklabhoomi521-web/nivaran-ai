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
python -m pytest -m paid_api     # tests that call paid APIs (only when you choose)
```

Secrets live in `.env` (git-ignored). Never commit them.
