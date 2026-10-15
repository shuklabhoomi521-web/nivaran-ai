# Phase 1 baseline: history of runs

(The file `baseline-phase1.md` is rewritten on every real run. This file keeps the story.)

## Runs (2026-10-15, `gemini-3.5-flash-lite`)
| Run | Prompt | Correct | Miss |
|---|---|---|---|
| 1 | original | 29/30 | `hg-05`: laptop labelled ecommerce (expected electronics_appliances) |
| 2 | + "category by what the problem is about, not where it was bought" (only `hg-05` re-run) | hg-05 fixed | other 29 not re-run |
| 3 | same as run 2, full re-run, cache cleared | 29/30 | `f-04`: "ticket cancel panniten, refund innum varala" got `railways` (expected `other`; the message does not say what kind of ticket) |

Reading: the prompt fix worked for `hg-05`, but one different problem flipped. Same prompt, different run, different answer, so results move a little between runs.
`f-04` is the AI guessing a category from the word "ticket". The company and the follow-up question were still right.
The table above is run 3 (the latest).

## Run 4: `category_confidence` (founder's decision instead of a forced "other")
- Change: new field `category_confidence` (high / low). Low means the AI is guessing; it must then ask a question.
  `f-04` now accepts `railways` **only if** confidence is low and a question is asked.
- Only `f-04` was re-run (to save free quota). Result: `railways`, confidence `low`, asked a question in Tamil -> pass.
- The other 29 are answers from run 3 (old prompt). They were given `category_confidence = high` only so the table could be built;
  they were **not** checked with the new prompt. So "30/30" in `baseline-phase1.md` is partly carried over.
- Note: the question for `f-04` asks which company or app it was, not explicitly what kind of ticket. It passes our check but could be sharper.

## Run 5: full re-run, cache cleared, nothing carried over (new question rule + confidence)
- Result: **28/30 correct (93%)**. Not 30/30.
- `f-04` passes and the question is better: "which company, and which kind of ticket (train, bus, or flight)?" (in Tamil).
- Miss `ta-06`: wrote `payment_method = 'SBI card'`. The user wrote "SBI கார்டு" in Tamil script. Not verbatim (it translated "கார்டு" to "card").
- Miss `f-02`: wrote `product = 'green kurti'`. The user wrote "greeen kurti" (typo). It fixed the spelling.
- Both misses are true facts restated, not made-up facts, but our rule is "copy exactly as typed", so they count as failures. Both passed in run 3: same prompt, different luck (run-to-run drift).
- Not changed: the scoring rule. Candidate fixes for later: tell the model again to copy typos and scripts unchanged, or relax the check to allow close spellings (needs the founder's decision).

## Run 5 re-scored with a new grading rule (founder's decision, no new API calls)
- Rule change (the prompt was NOT changed): exact copy is required only for ids, order/booking/claim numbers, phone numbers, amounts and dates.
  Other facts (product names, descriptions, payment method names) pass if they keep the same meaning (fixed typos and translated words are fine).
- Same 30 saved answers: **strict 28/30 (93%)**, **meaning-based 30/30 (100%)**. Both are kept in `docs/baseline-phase1.md`.
- The "same meaning" test is a cheap word-overlap check (no AI judge), so it is lenient. It would miss a wrong word if another word of the fact matches.

## Run-to-run drift (note for Phase 9)
- Same prompt, same model, different runs, different answers. Seen so far: `f-04` flipped category between run 1 and run 3; `ta-06` and `f-02` passed in run 3 but were restated in run 5.
- A single run of 30 problems is not a stable score. In Phase 9: run every problem 3-5 times, report the mean and the spread, and keep a stronger meaning judge.
