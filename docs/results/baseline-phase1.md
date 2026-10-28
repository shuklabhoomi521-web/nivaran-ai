# Phase 1 baseline (understand endpoint)

- Date: 2026-10-15
- Provider: `gemini`; model: `gemini-3.5-flash-lite`
- Problems: 30
- Same answers, scored two ways (no new API calls for the second):

| Rule | Correct (company, category, goal, facts) | Fully passed (plus safety and asking checks) |
|---|---|---|
| **Meaning-based (current rule)** | **30/30 (100%)** | 30/30 |
| Strict (old rule: every fact copied exactly) | 28/30 (93%) | 28/30 |

Meaning-based rule: ids, order/booking/claim numbers, phone numbers, amounts and dates must be copied exactly. Other facts (product names, descriptions, payment method names) pass if they keep the same meaning (fixed typos and translated words are fine). The check is a cheap word-overlap test, so it is lenient: Phase 9 should add a stronger judge.

## Meaning-based (current rule)

### Accuracy by language

| Group | Problems | Correct | Accuracy | Fully passed |
|---|---|---|---|---|
| english | 8 | 8 | 100% | 8/8 |
| hindi | 6 | 6 | 100% | 6/6 |
| hinglish | 8 | 8 | 100% | 8/8 |
| tamil | 8 | 8 | 100% | 8/8 |
| **All** | 30 | 30 | 100% | 30/30 |

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
| other | 1 | 1 | 100% | 1/1 |
| railways | 1 | 1 | 100% | 1/1 |
| telecom | 3 | 3 | 100% | 3/3 |
| utilities | 1 | 1 | 100% | 1/1 |
| **All** | 30 | 30 | 100% | 30/30 |

### Failures (meaning-based)

- none

## Strict (old rule), for comparison

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

### Failures (strict)

- `ta-06`: facts_grounded | invented fact: payment_method='SBI card'
- `f-02`: facts_grounded | invented fact: product='green kurti'
