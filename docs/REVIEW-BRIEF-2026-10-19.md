# Review brief for an independent checker (written 2026-10-19)

**Who this is for:** another Claude (or a human) who should check this project without trusting the author.
**Who wrote the work:** Claude (Sonnet 5.5) working with the founder (an ECE student). This brief was written by the same Claude that built the code, so treat every claim as *something to verify*, not as fact. Where I could not verify something I say so.

Repo: `~/nivaran` (private GitHub repo `shuklabhoomi521-web/nivaran`, branch `main`). Tags: `phase-0-done`, `phase-1-done`, `phase-2-done`. **Phase 3 is in progress and is not tagged.**

---

## 0. One-paragraph summary
Nivaran ("solution") is meant to be an app that handles customer care for a user: the user describes a problem once in their language; the app finds the company's official contact and (later) calls or emails for them. So far there is **no app, no phone call, no email**. What exists is a Python/FastAPI backend with: (Phase 1) an AI "brain" that turns a message into a structured case and a plan; (Phase 2) a hand-verified directory of 40 companies' official contacts with exact quotes, and a contact picker; (Phase 3, partial) speech interfaces and a speech-to-text bake-off. AI = Google Gemini free tier. The founder does not want to pay for any API.

## 1. Facts I re-checked just before writing this (commands run on 2026-10-19)
| Fact | How I checked | Result |
|---|---|---|
| Free tests pass | `cd backend && python -m pytest -q` | **284 passed**, 30 deselected (the 30 are `live_api` tests that call the real AI and are opt-in) |
| Tags | `git tag -l` | phase-0-done, phase-1-done, phase-2-done |
| Working tree clean, pushed | `git status -sb` | `main...origin/main`, no changes |
| No API key in tracked files | `git grep -n -I -E "AIza[0-9A-Za-z_-]{20,}\|sk-ant-..."` | no matches |
| `.env` not tracked | `git ls-files \| grep .env` | not tracked (`.gitignore` has it) |
| Directory size | read `backend/app/directory/companies.json` | 40 companies, 10 categories, 63 phone numbers, 48 emails |
| Quotes re-found by script | same file, `machine_checked` flag | **81 of 124** sources; the other 43 were read in a real browser by Claude (not machine-checked) |
| Phones on 2 official pages | same file | only **10 of 63** |
| Open gaps | same file | 13 `needs_check` items in 12 companies; Indian Railways has no contact at all |
| Repo visibility | `gh repo view nivaran --json visibility` | PRIVATE |

## 2. PRIVACY INCIDENT you should know about (found and partly fixed today)
While preparing this brief I found that commit `9dec69a` had **committed and pushed the founder's 10 raw voice recordings** (`speech_test/_incoming/my_recordings/*.aac` plus `sentences.json`) to the private GitHub repo. Cause: I ignored `speech_test/recordings/` but not the unzip folder `speech_test/_incoming/`.
- Fixed forward: files untracked, `speech_test/_incoming/` added to `.gitignore`, pushed (latest commit "Stop tracking the founder's raw voice recordings").
- **Not fixed:** the files are still in git history (commit `9dec69a`). Removing them needs a history rewrite and a force-push, which my rules forbid without the founder's explicit OK. The repo is private. The founder has been told in the chat (see end of this file for status).
- Checker: please confirm with `git ls-files | grep -E "\.aac$|_incoming"` (should print nothing) and `git log --all --oneline -- speech_test/_incoming` (will show the one commit).

(Also found: `CLAUDE.md` still said "Phase 2 done, waiting for OK to start Phase 3" while Phase 3 work was under way. Corrected on 2026-10-19. Checker: project state notes can lag behind the work.)

## 3. Rules the project says it follows (CLAUDE.md, docs/PLAN.md)
Key safety rules: never share/speak UPI PIN, card number, CVV, passwords, payment OTPs; only use contacts from a verified directory (official source + date; never from web search); AI must say it is an AI at the start of every call; user approves every email; private data encrypted; user can stop any action; reading apps/SMS is read-only.
**Implemented so far:** only a first version of the card/CVV/PIN stripper (`backend/app/safety/redact.py`) and the "contacts only from the directory" rule. **Not implemented yet (no code exists):** OTP handling, encryption at rest, call disclosure line, email approval, stop button, SMS/app reading. Those belong to Phases 4-8. Please do not credit the project with them.

## 4. Phase by phase: what was built, what is claimed, how to check, what is weak

### Phase 0: setup (tag `phase-0-done`)
Built: folder structure, FastAPI `/health`, one pytest, `.env.example`, README, CLAUDE.md, private repo. `/health` was verified with a live `uvicorn` + `curl` (200 `{"status":"ok"}`).
Weak: none notable. Phone provider interface exists as an abstract class only (`backend/app/channels/phone/base.py`).

### Phase 1: the brain, text only (tag `phase-1-done`)
Built: `POST /cases/understand` (message → `Case`), `POST /cases/plan`, `/chat` test page, card-number guard, rate limiter, scoring code, a 30-problem test set.
- AI: Gemini free tier, `gemini-3.5-flash-lite` (config in `.env`; Claude is an optional provider via `LLM_PROVIDER=anthropic`, **never run live**).
- Test set: 25 problems written by Claude + 5 messages written by the founder (`backend/tests/data/problems_core25.json`, `problems_founder5.json`). Languages: English, Hindi, Tamil, Hinglish.
- **Headline numbers (docs/baseline-phase1.md):** meaning-based **30/30**, strict **28/30**, from the same 30 saved answers of one run.
**Things a skeptical checker should weigh (all disclosed in docs/baseline-history.md):**
1. The grading rule was **loosened after seeing the results** (founder's decision): strict ("copy every fact exactly") 28/30 → meaning-based 30/30. The meaning check is a cheap word-overlap test with spelling tolerance (`backend/app/evaluation.py`, `fact_ok`), not a real judge; it can pass a fact if any one word overlaps.
2. A prompt rule about categories was added after a failure (laptop bought online counted as ecommerce). A `category_confidence` field (high/low, low must ask a question) was added at the founder's request, and one test's expected answer was widened by the founder (`f-04` accepts `railways` if confidence is low).
3. Results **drift between runs** (same prompt, same model): `f-04`, `ta-06`, `f-02` flipped. One run of 30 is not a stable score.
4. Small set, mostly author-written, so it may be easy. 30 problems cannot support "97%/100%" as real accuracy.
5. The saved AI answers (`docs/.live-cache-*.json`) are **not in git**, so the meaning-based re-score cannot be reproduced from the repo alone. `docs/baseline-phase1.json` has per-problem pass/fail and notes only.
6. `/cases/plan` has only ever run with a **fake AI** in tests. It was never called live. The `/chat` page was never opened in a browser by Claude (only `GET /chat` → 200).
How to check: `cd backend && python -m pytest -q`; read `app/evaluation.py` and `tests/test_evaluation.py`; run `python -m pytest -m live_api -s -q` (needs `GEMINI_API_KEY`, uses ~30 free requests, slow-limited, resumable) and compare to `docs/baseline-phase1.md`.

### Phase 2: company directory (tag `phase-2-done`)
Built: `companies.json` (40 companies), builder `scripts/build_directory.py` from hand-written `scripts/directory_src.py`, lookup by name/alias, picker (`app/directory/picker.py`), `/cases/plan` now returns the official contact and fixes impossible channels, verification checklist for the founder (`docs/directory-verification.md`), contact check on the 30 problems (`docs/phase2-contact-check.md`: 30/30 right company, 25/25 named-company problems have a verified contact).
How it works: each contact has `sources[]` with an official-domain URL and the **exact line** copied from the page; tests check HTTPS, official domain, date, that the number/email really appears inside its quote, and that every company has a contact or a `needs_check`.
**Weak / verify:**
1. A test that a number appears in its own quote cannot tell whether the quote is real. Only the builder's re-fetch (`machine_checked`, 81/124) or a human can. **Spot-check 10 random contacts against the live official pages**, especially the 43 browser-read ones. `python scripts/build_directory.py --refresh` re-fetches (network; many sites block scripts and will fail; that is expected).
2. The founder said they checked the list by hand (they confirmed Myntra and Ola personally). I cannot prove which boxes they ticked.
3. An "independent second check" file from the founder (`docs/second-check-2026-10-15.md`) was applied. One of its claims (old BSNL emails/number) **could not be reproduced**: that page now redirects to BSNL's home page. Those contacts were deliberately NOT added.
4. Swiggy, Zomato and Zepto officially say they have **no customer phone line**; this is recorded with the exact sentences. This is a product-level limit (the AI cannot phone them).
5. The picker is simple: first suitable phone by `role`/label. It does not look at the problem type (BSNL broadband vs mobile, etc.). Logged in `docs/TODO-research.md` for before Phase 5.
6. Numbers/names change; nothing monitors staleness.
7. Some entries came from search-assisted discovery of *page URLs*, but every stored contact was re-read from the official page. Please check `directory_src.py` has no number without a source tuple.

### Phase 3: voice in the browser (IN PROGRESS, not tagged, voice page NOT built)
Built so far: `app/speech/` (interfaces `SpeechToText`/`TextToSpeech`, Gemini providers, fakes, factory, audio conversion with macOS `afconvert`, scoring), `scripts/speech_bakeoff.py`, `scripts/prepare_public_clips.py`, `speech_test/` (sentences, README).
What the bake-off did: each clip heard 3 ways: clean 16 kHz, phone 8 kHz, phone mu-law. Clip sets: **own** (founder's 10 phone recordings: 5 Hinglish + 5 Indian English, 1 noisy each), **public** (Google FLEURS dev clips, CC-BY-4.0: 5 per language for Hindi, Tamil, US English, +1 noisy copy each made by adding other speakers' babble at 10 dB), **synthetic** (computer voice reads sentences, STT hears them back).
Latest results (docs/speech-bakeoff.md; STT = `gemini-3.5-flash-lite` prompted to transcribe, **with a language hint**):
| Real voices, quiet clips (WER) | Clean | 8 kHz | mu-law |
|---|---|---|---|
| Hinglish (own, 4 clips) | 77% (30% if extra words are ignored) | 83% (31%) | 83% (32%) |
| Indian English (own, 4 clips) | 10% | 7% | 10% |
| Hindi (FLEURS, 5) | 21% | 26% | 26% |
| Tamil (FLEURS, 5) | 38% | 51% | 31% |
| US English (FLEURS, 5) | 3% | 3% | 5% |
Numbers (4839201, 299, 1500, 2000, 40) were heard right in **30 of 30** checks across all three audio types. Noisy clips: Indian English 8%, Hinglish ~93-100% (the IRCTC clip was heard as "34077 ticket"/"University").
**Weak / verify (important):**
1. **Hinglish ground truth is soft.** In clips 1-3 the founder said extra or different words from the listed sentence, and I cannot listen to audio. The plain WER there is not meaningful; I added a "sentence found inside what was heard" score and a "phone vs clean transcript" agreement score (needs no ground truth). A human who speaks Hindi should read the transcripts in `docs/speech-bakeoff.json`.
2. **Tiny sample:** 4-5 clips per group. Treat percentages as rough.
3. **Tamil word error is inflated by Tamil's long words; character error is ~10-13%.** Also FLEURS sentences are formal Wikipedia-style read speech, not phone complaints.
4. **The language hint is an assumption:** the run tells the STT which language the user picked. Without the hint Tamil/Hindi were often written in the wrong script (see `docs/speech-bakeoff-no-hint.md`). The future app must supply the language (Phase 6 UI); phone calls in Phase 4 may not know it.
5. **Speed figures are wrong as a latency measure:** "median 10.1 s per call" includes our own rate-limit sleep (6 requests/minute). Real latency was not measured. The 1.5-second target is untested; non-streaming calls are likely too slow, streaming (Gemini Live) not tried.
6. **Dedicated Google speech models hang intermittently** (`gemini-3.5-transcribe`, `gemini-3.8-flash-tts`): calls sometimes never return and Google's own timeout setting did not stop them. A hard 75 s limit in a daemon thread was added (`app/speech/gemini.py`). A full run on the dedicated STT model was started and abandoned after hangs, so the two STT options were **not compared fairly**. The bake-off results above use the general model with a transcription prompt (`STT_PROVIDER=gemini_prompt`).
7. Computer-voice samples for Hindi/Tamil were generated with `gemini-3.8-flash-tts`; english/hinglish samples were regenerated after the founder's sentences replaced mine. Mixed generation dates; not important but note it.
8. **Free-tier privacy:** Google's pricing page says free-tier prompts/audio may be used to improve its products. Only test audio (public clips, founder's own voice) has been sent. Real users' data must never go through the free tier.
9. Audio conversion uses macOS `afconvert`; tests that need it skip on other systems.
10. WER normalisation (`app/speech/scoring.py`): lowercases, strips punctuation but keeps Indic vowel marks, turns number words into digits on both sides ("two thousand"="2000", "forty"="40"), merges digit runs, squeezes repeated letters. Hinglish is scored against both a Roman and a Devanagari reference (best of two), which favours the system. Please read the code and `tests/test_speech.py`.

## 5. Decisions the founder made (so you do not "fix" them)
- No paid APIs. Gemini free tier is the brain for now; own models replace it in Phase 9.
- Grading rule: exact copy only for ids/numbers/amounts/dates; meaning-based for the rest. Both scores are kept.
- Low category confidence must ask a question (instead of forcing "other").
- Supabase skipped until Phase 6; JSON file is the directory store.
- Phone: Twilio trial for Phase 4; Exotel KYC (with Udyam) is being asked about by email (no answer yet; see `docs/TODO-research.md`).
- Languages: Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi are a later "Phase 3.5" (after Phase 3). Currently only English, Hindi, Tamil, Hinglish are tested.
- Next step the founder picked: **try Sarvam (a paid-after-free-credits Indian speech provider) before building the voice page.** Not started. Unknown: free-credit amount and whether a card is needed.

## 6. Suggested independent checks, highest value first
1. `git ls-files | grep -E "\.aac$|_incoming|\.env$"` prints nothing; decide with the founder about purging history (section 2).
2. Run the free tests (284). Read the tests critically: do they check behaviour or just restate the code? (e.g. `test_picker.py`, `test_directory.py`, `test_speech.py`).
3. Try to break the card/PIN stripper (`app/safety/redact.py`): card numbers written with words, in other digit scripts, with dots, split over lines, inside Hindi/Tamil sentences, CVV/PIN words in Hindi/Tamil. Known limit: ASCII digits and English keywords only.
4. Spot-check 10 directory contacts against the live official pages (pick from the `machine_checked: false` ones). Check no contact lacks a source.
5. Read `app/evaluation.py`: is the meaning-based fact check too lenient? Try inventing a fact that shares one word with the message.
6. Re-run `python scripts/rescore_from_cache.py` only if you have the cache (not in git); otherwise re-run the live Phase 1 test (30 free requests) and see whether the score drifts.
7. Have someone who reads Hindi, Tamil and Hinglish read the transcripts in `docs/speech-bakeoff.json` against the audio and decide which errors are real.
8. Re-run the bake-off with a different seed/clips to see if the conclusions hold: `python scripts/prepare_public_clips.py` uses seed 17 and needs the FLEURS dev files re-downloaded (they were deleted).

## 7. Known gaps and honesty notes (summary)
- No end-to-end test through a real browser, phone or microphone.
- Safety layer is a first stub; most safety rules are still only rules on paper.
- Accuracy numbers come from small, author-written or tiny samples; one grading rule was relaxed after results.
- Directory: 43 of 124 sources not machine-verified; 10 of 63 phones with two sources; 12 companies with open gaps; staleness unmonitored.
- Speech: latency unmeasured; dedicated models unreliable; Hinglish references soft; hint assumption.
- Raw voice files exist in git history (private repo).

## 8. File map
- `backend/app/`: `brain/` (llm.py provider wrappers + rate limiter, understand.py, plan.py), `directory/` (models, loader, lookup, picker, companies.json), `speech/` (base, gemini, fakes, factory, audio, scoring), `safety/redact.py`, `models/`, `api/cases.py`, `evaluation.py`, `config.py`.
- `backend/tests/`: 14 test files (`pytest.ini` deselects `live_api`).
- `scripts/`: directory builder + page fetch/scan tools, bake-off, public-clip prep, contact check, rescore.
- `docs/`: PLAN.md (master plan), notes/phase-0..2.md, baseline-phase1.md/json + baseline-history.md, directory-verification.md, phase2-contact-check.md, speech-bakeoff*.md/json, gemini-free-tier.md, TODO-research.md, second-check-2026-10-15.md, this file.
- Not in git on purpose: `.env`, caches (`docs/.live-cache-*`, `docs/.speech-cache.json`, `scripts/.page_cache.json`), `speech_test/recordings|tts_samples|public|_incoming`.

## 9. How to run things
```bash
cd ~/nivaran && source .venv/bin/activate
cd backend && python -m pytest -q                     # 284 free tests
python -m pytest -m live_api -s -q                    # 30 real-AI tests (needs GEMINI_API_KEY in .env; slow-limited)
cd .. && python scripts/build_directory.py            # rebuild directory + checklist from scripts/directory_src.py (network)
STT_PROVIDER=gemini_prompt python scripts/speech_bakeoff.py --hint   # speech bake-off (needs key + macOS)
uvicorn app.main:app --reload --app-dir backend       # then open http://127.0.0.1:8000/chat
```
