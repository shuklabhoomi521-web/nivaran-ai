# Phase 1 baseline (understand endpoint)

- Date: 2026-10-15
- Provider: `gemini`; model: `gemini-3.5-flash-lite`
- Problems: 30; correct (company, category, goal, no invented facts): 28; fully passed (plus safety and asking checks): 28

### Accuracy by language

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| english | 8 | 8 | 100% | 8/8 |
| hindi | 6 | 6 | 100% | 6/6 |
| hinglish | 8 | 7 | 88% | 7/8 |
| tamil | 8 | 7 | 88% | 7/8 |
| **All** | 30 | 28 | 93% | 28/30 |

### Accuracy by category

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| airlines | 2 | 2 | 100% | 2/2 |
| banking_upi | 3 | 3 | 100% | 3/3 |
| cabs | 3 | 3 | 100% | 3/3 |
| ecommerce | 6 | 5 | 83% | 5/6 |
| electronics_appliances | 3 | 3 | 100% | 3/3 |
| food_delivery | 5 | 4 | 80% | 4/5 |
| insurance | 2 | 2 | 100% | 2/2 |
| other | 1 | 1 | 100% | 1/1 |
| railways | 1 | 1 | 100% | 1/1 |
| telecom | 3 | 3 | 100% | 3/3 |
| utilities | 1 | 1 | 100% | 1/1 |
| **All** | 30 | 28 | 93% | 28/30 |

### Failures

- `ta-06`: facts_grounded | invented fact: payment_method='SBI card'
- `f-02`: facts_grounded | invented fact: product='green kurti'
