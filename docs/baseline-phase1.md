# Phase 1 baseline (understand endpoint)

- Date: 2026-10-15
- Provider: `gemini`; model: `gemini-3.5-flash-lite`
- Problems: 30; correct (company, category, goal, no invented facts): 29; fully passed (plus safety and asking checks): 29

### Accuracy by language

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| english | 8 | 8 | 100% | 8/8 |
| hindi | 6 | 6 | 100% | 6/6 |
| hinglish | 8 | 8 | 100% | 8/8 |
| tamil | 8 | 7 | 88% | 7/8 |
| **All** | 30 | 29 | 97% | 29/30 |

### Accuracy by category

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| airlines | 2 | 2 | 100% | 2/2 |
| banking_upi | 3 | 3 | 100% | 3/3 |
| cabs | 3 | 3 | 100% | 3/3 |
| ecommerce | 6 | 6 | 100% | 6/6 |
| electronics_appliances | 3 | 3 | 100% | 3/3 |
| food_delivery | 5 | 5 | 100% | 5/5 |
| insurance | 2 | 2 | 100% | 2/2 |
| other | 1 | 0 | 0% | 0/1 |
| railways | 1 | 1 | 100% | 1/1 |
| telecom | 3 | 3 | 100% | 3/3 |
| utilities | 1 | 1 | 100% | 1/1 |
| **All** | 30 | 29 | 97% | 29/30 |

### Failures

- `f-04`: category

## History of runs (same day, `gemini-3.5-flash-lite`)
| Run | Prompt | Correct | Miss |
|---|---|---|---|
| 1 | original | 29/30 | `hg-05`: laptop labelled ecommerce (expected electronics_appliances) |
| 2 | + "category by what the problem is about, not where it was bought" (only `hg-05` re-run) | hg-05 fixed | other 29 not re-run |
| 3 | same as run 2, full re-run, cache cleared | 29/30 | `f-04`: "ticket cancel panniten, refund innum varala" got `railways` (expected `other`; the message does not say what kind of ticket) |

Reading: the prompt fix worked for `hg-05`, but one different problem flipped. Same prompt, different run, different answer, so results move a little between runs.
`f-04` is the AI guessing a category from the word "ticket". The company and the follow-up question were still right.
The table above is run 3 (the latest).
