# Phase 1 baseline (understand endpoint)

- Date: 2026-10-15
- Provider: `gemini`; model: `gemini-3.5-flash-lite`
- Problems: 30; correct (company, category, goal, no invented facts): 29; fully passed (plus safety and asking checks): 29

### Accuracy by language

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| english | 8 | 8 | 100% | 8/8 |
| hindi | 6 | 6 | 100% | 6/6 |
| hinglish | 8 | 7 | 88% | 7/8 |
| tamil | 8 | 8 | 100% | 8/8 |
| **All** | 30 | 29 | 97% | 29/30 |

### Accuracy by category

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| airlines | 2 | 2 | 100% | 2/2 |
| banking_upi | 3 | 3 | 100% | 3/3 |
| cabs | 3 | 3 | 100% | 3/3 |
| ecommerce | 6 | 6 | 100% | 6/6 |
| electronics_appliances | 3 | 2 | 67% | 2/3 |
| food_delivery | 5 | 5 | 100% | 5/5 |
| insurance | 2 | 2 | 100% | 2/2 |
| other | 1 | 1 | 100% | 1/1 |
| railways | 1 | 1 | 100% | 1/1 |
| telecom | 3 | 3 | 100% | 3/3 |
| utilities | 1 | 1 | 100% | 1/1 |
| **All** | 30 | 29 | 97% | 29/30 |

### Failures

- `hg-05`: category

## Addendum: category prompt fix (same day)
- Change: rule 2 of the understand prompt now says to choose the category by what the problem is about, not where it was bought.
- Re-run of `hg-05` only: before = `ecommerce` (wrong), after = `electronics_appliances` (correct). Company, goal and question unchanged.
- Score for the 30 problems: before 29/30 (97%); after 30/30 if no other problem changed. **Not verified**: the other 29 were not re-run with the new prompt.
  Risk to check: `en-02` (broken mixer grinder from Amazon, expected ecommerce) could now drift to electronics_appliances.
