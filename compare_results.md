# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date) rows |
|------|-----------------------------------|
| claude-opus-4.6 | 450 |
| claude-opus-4.7 | 432 |
| claude-sonnet-4.6 | 458 |
| deepseek-v4-flash | 422 |
| gemini-3.1-pro-preview | 474 |
| gpt-5.5 | 465 |
| willis | 388 |

- **Union across all files:** 851
- **Intersection across all files:** 171

---

## Pairwise Shared (matchup, page, date) Counts

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | gemini-3.1-pro-preview | gpt-5.5 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 450 | 367 | 387 | 357 | 371 | 379 | 208 |
| **claude-opus-4.7** | 367 | 432 | 362 | 316 | 345 | 358 | 208 |
| **claude-sonnet-4.6** | 387 | 362 | 458 | 356 | 389 | 380 | 204 |
| **deepseek-v4-flash** | 357 | 316 | 356 | 422 | 353 | 353 | 200 |
| **gemini-3.1-pro-preview** | 371 | 345 | 389 | 353 | 474 | 364 | 190 |
| **gpt-5.5** | 379 | 358 | 380 | 353 | 364 | 465 | 214 |
| **willis** | 208 | 208 | 204 | 200 | 190 | 214 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | gemini-3.1-pro-preview | gpt-5.5 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 1.000 | 0.713 | 0.743 | 0.693 | 0.671 | 0.707 | 0.330 |
| **claude-opus-4.7** | 0.713 | 1.000 | 0.686 | 0.587 | 0.615 | 0.664 | 0.340 |
| **claude-sonnet-4.6** | 0.743 | 0.686 | 1.000 | 0.679 | 0.716 | 0.700 | 0.318 |
| **deepseek-v4-flash** | 0.693 | 0.587 | 0.679 | 1.000 | 0.650 | 0.661 | 0.328 |
| **gemini-3.1-pro-preview** | 0.671 | 0.615 | 0.716 | 0.650 | 1.000 | 0.633 | 0.283 |
| **gpt-5.5** | 0.707 | 0.664 | 0.700 | 0.661 | 0.633 | 1.000 | 0.335 |
| **willis** | 0.330 | 0.340 | 0.318 | 0.328 | 0.283 | 0.335 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| claude-opus-4.6 vs claude-opus-4.7 | 83 | 65 |
| claude-opus-4.6 vs claude-sonnet-4.6 | 63 | 71 |
| claude-opus-4.6 vs deepseek-v4-flash | 93 | 65 |
| claude-opus-4.6 vs gemini-3.1-pro-preview | 79 | 103 |
| claude-opus-4.6 vs gpt-5.5 | 71 | 86 |
| claude-opus-4.6 vs willis | 242 | 180 |
| claude-opus-4.7 vs claude-sonnet-4.6 | 70 | 96 |
| claude-opus-4.7 vs deepseek-v4-flash | 116 | 106 |
| claude-opus-4.7 vs gemini-3.1-pro-preview | 87 | 129 |
| claude-opus-4.7 vs gpt-5.5 | 74 | 107 |
| claude-opus-4.7 vs willis | 224 | 180 |
| claude-sonnet-4.6 vs deepseek-v4-flash | 102 | 66 |
| claude-sonnet-4.6 vs gemini-3.1-pro-preview | 69 | 85 |
| claude-sonnet-4.6 vs gpt-5.5 | 78 | 85 |
| claude-sonnet-4.6 vs willis | 254 | 184 |
| deepseek-v4-flash vs gemini-3.1-pro-preview | 69 | 121 |
| deepseek-v4-flash vs gpt-5.5 | 69 | 112 |
| deepseek-v4-flash vs willis | 222 | 188 |
| gemini-3.1-pro-preview vs gpt-5.5 | 110 | 101 |
| gemini-3.1-pro-preview vs willis | 284 | 198 |
| gpt-5.5 vs willis | 251 | 174 |

---

## Agreement Distribution

How many of the 7 files agree on each unique (matchup, page, date) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 7 | 319 |
| 2 / 7 | 65 |
| 3 / 7 | 59 |
| 4 / 7 | 53 |
| 5 / 7 | 50 |
| 6 / 7 | 134 |
| 7 / 7 | 171 |
