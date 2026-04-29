# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date) rows |
|------|-----------------------------------|
| claude-opus-4.6 | 450 |
| claude-opus-4.7 | 432 |
| claude-sonnet-4.6 | 458 |
| deepseek-v4-flash | 422 |
| deepseek-v4-pro | 452 |
| gemini-3.1-pro-preview | 474 |
| glm-5_cloud | 461 |
| gpt-5.5 | 465 |
| minimax-m2.7 | 439 |
| mistral-large-3_675b-cloud | 509 |
| qwen3.6_35b-a3b-mlx-bf16 | 160 |
| willis | 388 |

- **Union across all files:** 1,126
- **Intersection across all files:** 39

---

## Pairwise Shared (matchup, page, date) Counts

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | deepseek-v4-pro | gemini-3.1-pro-preview | glm-5_cloud | gpt-5.5 | minimax-m2.7 | mistral-large-3_675b-cloud | qwen3.6_35b-a3b-mlx-bf16 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 450 | 367 | 387 | 357 | 346 | 371 | 348 | 379 | 310 | 330 | 109 | 208 |
| **claude-opus-4.7** | 367 | 432 | 362 | 316 | 316 | 345 | 328 | 358 | 272 | 312 | 100 | 208 |
| **claude-sonnet-4.6** | 387 | 362 | 458 | 356 | 354 | 389 | 374 | 380 | 314 | 341 | 105 | 204 |
| **deepseek-v4-flash** | 357 | 316 | 356 | 422 | 336 | 353 | 334 | 353 | 319 | 318 | 104 | 200 |
| **deepseek-v4-pro** | 346 | 316 | 354 | 336 | 452 | 368 | 346 | 346 | 304 | 333 | 96 | 186 |
| **gemini-3.1-pro-preview** | 371 | 345 | 389 | 353 | 368 | 474 | 377 | 364 | 302 | 349 | 108 | 190 |
| **glm-5_cloud** | 348 | 328 | 374 | 334 | 346 | 377 | 461 | 342 | 312 | 354 | 80 | 197 |
| **gpt-5.5** | 379 | 358 | 380 | 353 | 346 | 364 | 342 | 465 | 291 | 341 | 101 | 214 |
| **minimax-m2.7** | 310 | 272 | 314 | 319 | 304 | 302 | 312 | 291 | 439 | 277 | 80 | 180 |
| **mistral-large-3_675b-cloud** | 330 | 312 | 341 | 318 | 333 | 349 | 354 | 341 | 277 | 509 | 90 | 187 |
| **qwen3.6_35b-a3b-mlx-bf16** | 109 | 100 | 105 | 104 | 96 | 108 | 80 | 101 | 80 | 90 | 160 | 43 |
| **willis** | 208 | 208 | 204 | 200 | 186 | 190 | 197 | 214 | 180 | 187 | 43 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | deepseek-v4-pro | gemini-3.1-pro-preview | glm-5_cloud | gpt-5.5 | minimax-m2.7 | mistral-large-3_675b-cloud | qwen3.6_35b-a3b-mlx-bf16 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 1.000 | 0.713 | 0.743 | 0.693 | 0.622 | 0.671 | 0.618 | 0.707 | 0.535 | 0.525 | 0.218 | 0.330 |
| **claude-opus-4.7** | 0.713 | 1.000 | 0.686 | 0.587 | 0.556 | 0.615 | 0.581 | 0.664 | 0.454 | 0.496 | 0.203 | 0.340 |
| **claude-sonnet-4.6** | 0.743 | 0.686 | 1.000 | 0.679 | 0.637 | 0.716 | 0.686 | 0.700 | 0.539 | 0.545 | 0.205 | 0.318 |
| **deepseek-v4-flash** | 0.693 | 0.587 | 0.679 | 1.000 | 0.625 | 0.650 | 0.608 | 0.661 | 0.589 | 0.519 | 0.218 | 0.328 |
| **deepseek-v4-pro** | 0.622 | 0.556 | 0.637 | 0.625 | 1.000 | 0.659 | 0.610 | 0.606 | 0.518 | 0.530 | 0.186 | 0.284 |
| **gemini-3.1-pro-preview** | 0.671 | 0.615 | 0.716 | 0.650 | 0.659 | 1.000 | 0.676 | 0.633 | 0.494 | 0.550 | 0.205 | 0.283 |
| **glm-5_cloud** | 0.618 | 0.581 | 0.686 | 0.608 | 0.610 | 0.676 | 1.000 | 0.586 | 0.531 | 0.575 | 0.148 | 0.302 |
| **gpt-5.5** | 0.707 | 0.664 | 0.700 | 0.661 | 0.606 | 0.633 | 0.586 | 1.000 | 0.475 | 0.539 | 0.193 | 0.335 |
| **minimax-m2.7** | 0.535 | 0.454 | 0.539 | 0.589 | 0.518 | 0.494 | 0.531 | 0.475 | 1.000 | 0.413 | 0.154 | 0.278 |
| **mistral-large-3_675b-cloud** | 0.525 | 0.496 | 0.545 | 0.519 | 0.530 | 0.550 | 0.575 | 0.539 | 0.413 | 1.000 | 0.155 | 0.263 |
| **qwen3.6_35b-a3b-mlx-bf16** | 0.218 | 0.203 | 0.205 | 0.218 | 0.186 | 0.205 | 0.148 | 0.193 | 0.154 | 0.155 | 1.000 | 0.085 |
| **willis** | 0.330 | 0.340 | 0.318 | 0.328 | 0.284 | 0.283 | 0.302 | 0.335 | 0.278 | 0.263 | 0.085 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| claude-opus-4.6 vs claude-opus-4.7 | 83 | 65 |
| claude-opus-4.6 vs claude-sonnet-4.6 | 63 | 71 |
| claude-opus-4.6 vs deepseek-v4-flash | 93 | 65 |
| claude-opus-4.6 vs deepseek-v4-pro | 104 | 106 |
| claude-opus-4.6 vs gemini-3.1-pro-preview | 79 | 103 |
| claude-opus-4.6 vs glm-5_cloud | 102 | 113 |
| claude-opus-4.6 vs gpt-5.5 | 71 | 86 |
| claude-opus-4.6 vs minimax-m2.7 | 140 | 129 |
| claude-opus-4.6 vs mistral-large-3_675b-cloud | 120 | 179 |
| claude-opus-4.6 vs qwen3.6_35b-a3b-mlx-bf16 | 341 | 51 |
| claude-opus-4.6 vs willis | 242 | 180 |
| claude-opus-4.7 vs claude-sonnet-4.6 | 70 | 96 |
| claude-opus-4.7 vs deepseek-v4-flash | 116 | 106 |
| claude-opus-4.7 vs deepseek-v4-pro | 116 | 136 |
| claude-opus-4.7 vs gemini-3.1-pro-preview | 87 | 129 |
| claude-opus-4.7 vs glm-5_cloud | 104 | 133 |
| claude-opus-4.7 vs gpt-5.5 | 74 | 107 |
| claude-opus-4.7 vs minimax-m2.7 | 160 | 167 |
| claude-opus-4.7 vs mistral-large-3_675b-cloud | 120 | 197 |
| claude-opus-4.7 vs qwen3.6_35b-a3b-mlx-bf16 | 332 | 60 |
| claude-opus-4.7 vs willis | 224 | 180 |
| claude-sonnet-4.6 vs deepseek-v4-flash | 102 | 66 |
| claude-sonnet-4.6 vs deepseek-v4-pro | 104 | 98 |
| claude-sonnet-4.6 vs gemini-3.1-pro-preview | 69 | 85 |
| claude-sonnet-4.6 vs glm-5_cloud | 84 | 87 |
| claude-sonnet-4.6 vs gpt-5.5 | 78 | 85 |
| claude-sonnet-4.6 vs minimax-m2.7 | 144 | 125 |
| claude-sonnet-4.6 vs mistral-large-3_675b-cloud | 117 | 168 |
| claude-sonnet-4.6 vs qwen3.6_35b-a3b-mlx-bf16 | 353 | 55 |
| claude-sonnet-4.6 vs willis | 254 | 184 |
| deepseek-v4-flash vs deepseek-v4-pro | 86 | 116 |
| deepseek-v4-flash vs gemini-3.1-pro-preview | 69 | 121 |
| deepseek-v4-flash vs glm-5_cloud | 88 | 127 |
| deepseek-v4-flash vs gpt-5.5 | 69 | 112 |
| deepseek-v4-flash vs minimax-m2.7 | 103 | 120 |
| deepseek-v4-flash vs mistral-large-3_675b-cloud | 104 | 191 |
| deepseek-v4-flash vs qwen3.6_35b-a3b-mlx-bf16 | 318 | 56 |
| deepseek-v4-flash vs willis | 222 | 188 |
| deepseek-v4-pro vs gemini-3.1-pro-preview | 84 | 106 |
| deepseek-v4-pro vs glm-5_cloud | 106 | 115 |
| deepseek-v4-pro vs gpt-5.5 | 106 | 119 |
| deepseek-v4-pro vs minimax-m2.7 | 148 | 135 |
| deepseek-v4-pro vs mistral-large-3_675b-cloud | 119 | 176 |
| deepseek-v4-pro vs qwen3.6_35b-a3b-mlx-bf16 | 356 | 64 |
| deepseek-v4-pro vs willis | 266 | 202 |
| gemini-3.1-pro-preview vs glm-5_cloud | 97 | 84 |
| gemini-3.1-pro-preview vs gpt-5.5 | 110 | 101 |
| gemini-3.1-pro-preview vs minimax-m2.7 | 172 | 137 |
| gemini-3.1-pro-preview vs mistral-large-3_675b-cloud | 125 | 160 |
| gemini-3.1-pro-preview vs qwen3.6_35b-a3b-mlx-bf16 | 366 | 52 |
| gemini-3.1-pro-preview vs willis | 284 | 198 |
| glm-5_cloud vs gpt-5.5 | 119 | 123 |
| glm-5_cloud vs minimax-m2.7 | 149 | 127 |
| glm-5_cloud vs mistral-large-3_675b-cloud | 107 | 155 |
| glm-5_cloud vs qwen3.6_35b-a3b-mlx-bf16 | 381 | 80 |
| glm-5_cloud vs willis | 264 | 191 |
| gpt-5.5 vs minimax-m2.7 | 174 | 148 |
| gpt-5.5 vs mistral-large-3_675b-cloud | 124 | 168 |
| gpt-5.5 vs qwen3.6_35b-a3b-mlx-bf16 | 364 | 59 |
| gpt-5.5 vs willis | 251 | 174 |
| minimax-m2.7 vs mistral-large-3_675b-cloud | 162 | 232 |
| minimax-m2.7 vs qwen3.6_35b-a3b-mlx-bf16 | 359 | 80 |
| minimax-m2.7 vs willis | 259 | 208 |
| mistral-large-3_675b-cloud vs qwen3.6_35b-a3b-mlx-bf16 | 419 | 70 |
| mistral-large-3_675b-cloud vs willis | 322 | 201 |
| qwen3.6_35b-a3b-mlx-bf16 vs willis | 117 | 345 |

---

## Agreement Distribution

How many of the 7 files agree on each unique (matchup, page, date) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 12 | 490 |
| 2 / 12 | 92 |
| 3 / 12 | 47 |
| 4 / 12 | 56 |
| 5 / 12 | 40 |
| 6 / 12 | 31 |
| 7 / 12 | 30 |
| 8 / 12 | 35 |
| 9 / 12 | 63 |
| 10 / 12 | 73 |
| 11 / 12 | 130 |
| 12 / 12 | 39 |
