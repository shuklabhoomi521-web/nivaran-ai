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
