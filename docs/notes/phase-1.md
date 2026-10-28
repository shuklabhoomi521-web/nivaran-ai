# Phase 1 notes: the brain, text only

## Summary (5 lines)
- Built: `/cases/understand` and `/cases/plan` (Gemini free tier by default, Claude optional), chat page, card-number guard, rate limiter, scoring code.
- Result: 29/30 correct on the real run (`gemini-3.5-flash-lite`); table in `docs/results/baseline-phase1.md`. This is the Phase 9 baseline.
- Broke: Google "server busy" (503) stopped the first run; fixed with retries. One category miss fixed with a prompt rule; a different one (`f-04`) flipped.
- Learned: results move a little between runs, and a vague word like "ticket" makes the model guess a category.
- Tagged `phase-1-done` with the 29/30 marked **partly done** (founder's decision).

## Done-when check
| Item | Status | Proof |
|---|---|---|
| All 30 test problems become correct cases | **Partly**: 29/30 | `docs/results/baseline-phase1.md` (miss: `f-04` got `railways`, expected `other`) |
| Missing details are asked, never invented | Done on this set | `facts_grounded` and `asks_when_*` checks passed for all 30 |
| All tests pass | Done | 44 free tests pass (`python -m pytest`); real run: 29 of 30 |

## 3 weakest parts
1. Guesses from vague words (`f-04`). Fix: rule "too vague to tell the category means `other`", then re-run all 30.
2. Small test set, mostly written by me; run-to-run drift. Fix: grow to 100+ problems with real anonymised cases and run each 3 times.
3. Free tier: 503s, unknown daily limits, and Google may train on free-tier prompts. Fix: test data only; before real users use a paid tier or our own models (Phase 9).

## Demo clip (30 seconds)
Open `http://127.0.0.1:8000/chat`. Type the Tamil-in-English-letters message "ticket cancel panniten, refund innum varala": show the follow-up question in Tamil. Then type a message with a card number and show "For safety I removed: card_number".
