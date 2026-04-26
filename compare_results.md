# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date) rows |
|------|-----------------------------------|
| claude-opus-4.6 | 450 |
| claude-opus-4.7 | 432 |
| claude-sonnet-4.6 | 458 |
| gemini-3.1-pro-preview | 474 |
| gpt-5.5 | 465 |
| willis | 388 |

- **Union across all files:** 819
- **Intersection across all files:** 175

---

## Pairwise Shared (matchup, page, date) Counts

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | gemini-3.1-pro-preview | gpt-5.5 | willis |
| -- | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 450 | 367 | 387 | 371 | 379 | 208 |
| **claude-opus-4.7** | 367 | 432 | 362 | 345 | 358 | 208 |
| **claude-sonnet-4.6** | 387 | 362 | 458 | 389 | 380 | 204 |
| **gemini-3.1-pro-preview** | 371 | 345 | 389 | 474 | 364 | 190 |
| **gpt-5.5** | 379 | 358 | 380 | 364 | 465 | 214 |
| **willis** | 208 | 208 | 204 | 190 | 214 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | gemini-3.1-pro-preview | gpt-5.5 | willis |
| -- | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 1.000 | 0.713 | 0.743 | 0.671 | 0.707 | 0.330 |
| **claude-opus-4.7** | 0.713 | 1.000 | 0.686 | 0.615 | 0.664 | 0.340 |
| **claude-sonnet-4.6** | 0.743 | 0.686 | 1.000 | 0.716 | 0.700 | 0.318 |
| **gemini-3.1-pro-preview** | 0.671 | 0.615 | 0.716 | 1.000 | 0.633 | 0.283 |
| **gpt-5.5** | 0.707 | 0.664 | 0.700 | 0.633 | 1.000 | 0.335 |
| **willis** | 0.330 | 0.340 | 0.318 | 0.283 | 0.335 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| claude-opus-4.6 vs claude-opus-4.7 | 83 | 65 |
| claude-opus-4.6 vs claude-sonnet-4.6 | 63 | 71 |
| claude-opus-4.6 vs gemini-3.1-pro-preview | 79 | 103 |
| claude-opus-4.6 vs gpt-5.5 | 71 | 86 |
| claude-opus-4.6 vs willis | 242 | 180 |
| claude-opus-4.7 vs claude-sonnet-4.6 | 70 | 96 |
| claude-opus-4.7 vs gemini-3.1-pro-preview | 87 | 129 |
| claude-opus-4.7 vs gpt-5.5 | 74 | 107 |
| claude-opus-4.7 vs willis | 224 | 180 |
| claude-sonnet-4.6 vs gemini-3.1-pro-preview | 69 | 85 |
| claude-sonnet-4.6 vs gpt-5.5 | 78 | 85 |
| claude-sonnet-4.6 vs willis | 254 | 184 |
| gemini-3.1-pro-preview vs gpt-5.5 | 110 | 101 |
| gemini-3.1-pro-preview vs willis | 284 | 198 |
| gpt-5.5 vs willis | 251 | 174 |

---

## Agreement Distribution

How many of the 7 files agree on each unique (matchup, page, date) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 6 | 298 |
| 2 / 6 | 79 |
| 3 / 6 | 48 |
| 4 / 6 | 78 |
| 5 / 6 | 141 |
| 6 / 6 | 175 |
