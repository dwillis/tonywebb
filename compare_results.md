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
| kimi-k2.6 | 429 |
| minimax-m2.7 | 439 |
| mistral-large-3_675b-cloud | 509 |
| qwen3.6_35b-a3b-mlx-bf16 | 422 |
| willis | 388 |

- **Union across all files:** 1,260
- **Intersection across all files:** 103

---

## Pairwise Shared (matchup, page, date) Counts

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | deepseek-v4-pro | gemini-3.1-pro-preview | glm-5_cloud | gpt-5.5 | kimi-k2.6 | minimax-m2.7 | mistral-large-3_675b-cloud | qwen3.6_35b-a3b-mlx-bf16 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 450 | 367 | 387 | 357 | 346 | 371 | 348 | 379 | 311 | 310 | 330 | 211 | 208 |
| **claude-opus-4.7** | 367 | 432 | 362 | 316 | 316 | 345 | 328 | 358 | 284 | 272 | 312 | 197 | 208 |
| **claude-sonnet-4.6** | 387 | 362 | 458 | 356 | 354 | 389 | 374 | 380 | 335 | 314 | 341 | 213 | 204 |
| **deepseek-v4-flash** | 357 | 316 | 356 | 422 | 336 | 353 | 334 | 353 | 304 | 319 | 318 | 211 | 200 |
| **deepseek-v4-pro** | 346 | 316 | 354 | 336 | 452 | 368 | 346 | 346 | 318 | 304 | 333 | 222 | 186 |
| **gemini-3.1-pro-preview** | 371 | 345 | 389 | 353 | 368 | 474 | 377 | 364 | 321 | 302 | 349 | 213 | 190 |
| **glm-5_cloud** | 348 | 328 | 374 | 334 | 346 | 377 | 461 | 342 | 344 | 312 | 354 | 193 | 197 |
| **gpt-5.5** | 379 | 358 | 380 | 353 | 346 | 364 | 342 | 465 | 306 | 291 | 341 | 228 | 214 |
| **kimi-k2.6** | 311 | 284 | 335 | 304 | 318 | 321 | 344 | 306 | 429 | 294 | 311 | 193 | 171 |
| **minimax-m2.7** | 310 | 272 | 314 | 319 | 304 | 302 | 312 | 291 | 294 | 439 | 277 | 182 | 180 |
| **mistral-large-3_675b-cloud** | 330 | 312 | 341 | 318 | 333 | 349 | 354 | 341 | 311 | 277 | 509 | 202 | 187 |
| **qwen3.6_35b-a3b-mlx-bf16** | 211 | 197 | 213 | 211 | 222 | 213 | 193 | 228 | 193 | 182 | 202 | 422 | 123 |
| **willis** | 208 | 208 | 204 | 200 | 186 | 190 | 197 | 214 | 171 | 180 | 187 | 123 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | claude-opus-4.6 | claude-opus-4.7 | claude-sonnet-4.6 | deepseek-v4-flash | deepseek-v4-pro | gemini-3.1-pro-preview | glm-5_cloud | gpt-5.5 | kimi-k2.6 | minimax-m2.7 | mistral-large-3_675b-cloud | qwen3.6_35b-a3b-mlx-bf16 | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **claude-opus-4.6** | 1.000 | 0.713 | 0.743 | 0.693 | 0.622 | 0.671 | 0.618 | 0.707 | 0.548 | 0.535 | 0.525 | 0.319 | 0.330 |
| **claude-opus-4.7** | 0.713 | 1.000 | 0.686 | 0.587 | 0.556 | 0.615 | 0.581 | 0.664 | 0.492 | 0.454 | 0.496 | 0.300 | 0.340 |
| **claude-sonnet-4.6** | 0.743 | 0.686 | 1.000 | 0.679 | 0.637 | 0.716 | 0.686 | 0.700 | 0.607 | 0.539 | 0.545 | 0.319 | 0.318 |
| **deepseek-v4-flash** | 0.693 | 0.587 | 0.679 | 1.000 | 0.625 | 0.650 | 0.608 | 0.661 | 0.556 | 0.589 | 0.519 | 0.333 | 0.328 |
| **deepseek-v4-pro** | 0.622 | 0.556 | 0.637 | 0.625 | 1.000 | 0.659 | 0.610 | 0.606 | 0.565 | 0.518 | 0.530 | 0.340 | 0.284 |
| **gemini-3.1-pro-preview** | 0.671 | 0.615 | 0.716 | 0.650 | 0.659 | 1.000 | 0.676 | 0.633 | 0.552 | 0.494 | 0.550 | 0.312 | 0.283 |
| **glm-5_cloud** | 0.618 | 0.581 | 0.686 | 0.608 | 0.610 | 0.676 | 1.000 | 0.586 | 0.630 | 0.531 | 0.575 | 0.280 | 0.302 |
| **gpt-5.5** | 0.707 | 0.664 | 0.700 | 0.661 | 0.606 | 0.633 | 0.586 | 1.000 | 0.520 | 0.475 | 0.539 | 0.346 | 0.335 |
| **kimi-k2.6** | 0.548 | 0.492 | 0.607 | 0.556 | 0.565 | 0.552 | 0.630 | 0.520 | 1.000 | 0.512 | 0.496 | 0.293 | 0.265 |
| **minimax-m2.7** | 0.535 | 0.454 | 0.539 | 0.589 | 0.518 | 0.494 | 0.531 | 0.475 | 0.512 | 1.000 | 0.413 | 0.268 | 0.278 |
| **mistral-large-3_675b-cloud** | 0.525 | 0.496 | 0.545 | 0.519 | 0.530 | 0.550 | 0.575 | 0.539 | 0.496 | 0.413 | 1.000 | 0.277 | 0.263 |
| **qwen3.6_35b-a3b-mlx-bf16** | 0.319 | 0.300 | 0.319 | 0.333 | 0.340 | 0.312 | 0.280 | 0.346 | 0.293 | 0.268 | 0.277 | 1.000 | 0.179 |
| **willis** | 0.330 | 0.340 | 0.318 | 0.328 | 0.284 | 0.283 | 0.302 | 0.335 | 0.265 | 0.278 | 0.263 | 0.179 | 1.000 |

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
| claude-opus-4.6 vs kimi-k2.6 | 139 | 118 |
| claude-opus-4.6 vs minimax-m2.7 | 140 | 129 |
| claude-opus-4.6 vs mistral-large-3_675b-cloud | 120 | 179 |
| claude-opus-4.6 vs qwen3.6_35b-a3b-mlx-bf16 | 239 | 211 |
| claude-opus-4.6 vs willis | 242 | 180 |
| claude-opus-4.7 vs claude-sonnet-4.6 | 70 | 96 |
| claude-opus-4.7 vs deepseek-v4-flash | 116 | 106 |
| claude-opus-4.7 vs deepseek-v4-pro | 116 | 136 |
| claude-opus-4.7 vs gemini-3.1-pro-preview | 87 | 129 |
| claude-opus-4.7 vs glm-5_cloud | 104 | 133 |
| claude-opus-4.7 vs gpt-5.5 | 74 | 107 |
| claude-opus-4.7 vs kimi-k2.6 | 148 | 145 |
| claude-opus-4.7 vs minimax-m2.7 | 160 | 167 |
| claude-opus-4.7 vs mistral-large-3_675b-cloud | 120 | 197 |
| claude-opus-4.7 vs qwen3.6_35b-a3b-mlx-bf16 | 235 | 225 |
| claude-opus-4.7 vs willis | 224 | 180 |
| claude-sonnet-4.6 vs deepseek-v4-flash | 102 | 66 |
| claude-sonnet-4.6 vs deepseek-v4-pro | 104 | 98 |
| claude-sonnet-4.6 vs gemini-3.1-pro-preview | 69 | 85 |
| claude-sonnet-4.6 vs glm-5_cloud | 84 | 87 |
| claude-sonnet-4.6 vs gpt-5.5 | 78 | 85 |
| claude-sonnet-4.6 vs kimi-k2.6 | 123 | 94 |
| claude-sonnet-4.6 vs minimax-m2.7 | 144 | 125 |
| claude-sonnet-4.6 vs mistral-large-3_675b-cloud | 117 | 168 |
| claude-sonnet-4.6 vs qwen3.6_35b-a3b-mlx-bf16 | 245 | 209 |
| claude-sonnet-4.6 vs willis | 254 | 184 |
| deepseek-v4-flash vs deepseek-v4-pro | 86 | 116 |
| deepseek-v4-flash vs gemini-3.1-pro-preview | 69 | 121 |
| deepseek-v4-flash vs glm-5_cloud | 88 | 127 |
| deepseek-v4-flash vs gpt-5.5 | 69 | 112 |
| deepseek-v4-flash vs kimi-k2.6 | 118 | 125 |
| deepseek-v4-flash vs minimax-m2.7 | 103 | 120 |
| deepseek-v4-flash vs mistral-large-3_675b-cloud | 104 | 191 |
| deepseek-v4-flash vs qwen3.6_35b-a3b-mlx-bf16 | 211 | 211 |
| deepseek-v4-flash vs willis | 222 | 188 |
| deepseek-v4-pro vs gemini-3.1-pro-preview | 84 | 106 |
| deepseek-v4-pro vs glm-5_cloud | 106 | 115 |
| deepseek-v4-pro vs gpt-5.5 | 106 | 119 |
| deepseek-v4-pro vs kimi-k2.6 | 134 | 111 |
| deepseek-v4-pro vs minimax-m2.7 | 148 | 135 |
| deepseek-v4-pro vs mistral-large-3_675b-cloud | 119 | 176 |
| deepseek-v4-pro vs qwen3.6_35b-a3b-mlx-bf16 | 230 | 200 |
| deepseek-v4-pro vs willis | 266 | 202 |
| gemini-3.1-pro-preview vs glm-5_cloud | 97 | 84 |
| gemini-3.1-pro-preview vs gpt-5.5 | 110 | 101 |
| gemini-3.1-pro-preview vs kimi-k2.6 | 153 | 108 |
| gemini-3.1-pro-preview vs minimax-m2.7 | 172 | 137 |
| gemini-3.1-pro-preview vs mistral-large-3_675b-cloud | 125 | 160 |
| gemini-3.1-pro-preview vs qwen3.6_35b-a3b-mlx-bf16 | 261 | 209 |
| gemini-3.1-pro-preview vs willis | 284 | 198 |
| glm-5_cloud vs gpt-5.5 | 119 | 123 |
| glm-5_cloud vs kimi-k2.6 | 117 | 85 |
| glm-5_cloud vs minimax-m2.7 | 149 | 127 |
| glm-5_cloud vs mistral-large-3_675b-cloud | 107 | 155 |
| glm-5_cloud vs qwen3.6_35b-a3b-mlx-bf16 | 268 | 229 |
| glm-5_cloud vs willis | 264 | 191 |
| gpt-5.5 vs kimi-k2.6 | 159 | 123 |
| gpt-5.5 vs minimax-m2.7 | 174 | 148 |
| gpt-5.5 vs mistral-large-3_675b-cloud | 124 | 168 |
| gpt-5.5 vs qwen3.6_35b-a3b-mlx-bf16 | 237 | 194 |
| gpt-5.5 vs willis | 251 | 174 |
| kimi-k2.6 vs minimax-m2.7 | 135 | 145 |
| kimi-k2.6 vs mistral-large-3_675b-cloud | 118 | 198 |
| kimi-k2.6 vs qwen3.6_35b-a3b-mlx-bf16 | 236 | 229 |
| kimi-k2.6 vs willis | 258 | 217 |
| minimax-m2.7 vs mistral-large-3_675b-cloud | 162 | 232 |
| minimax-m2.7 vs qwen3.6_35b-a3b-mlx-bf16 | 257 | 240 |
| minimax-m2.7 vs willis | 259 | 208 |
| mistral-large-3_675b-cloud vs qwen3.6_35b-a3b-mlx-bf16 | 307 | 220 |
| mistral-large-3_675b-cloud vs willis | 322 | 201 |
| qwen3.6_35b-a3b-mlx-bf16 vs willis | 299 | 265 |

---

## Agreement Distribution

How many of the 7 files agree on each unique (matchup, page, date) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 13 | 570 |
| 2 / 13 | 121 |
| 3 / 13 | 49 |
| 4 / 13 | 65 |
| 5 / 13 | 29 |
| 6 / 13 | 41 |
| 7 / 13 | 25 |
| 8 / 13 | 38 |
| 9 / 13 | 38 |
| 10 / 13 | 43 |
| 11 / 13 | 55 |
| 12 / 13 | 83 |
| 13 / 13 | 103 |
