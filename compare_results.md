# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date, content_type) rows |
|------|---------------------------------------------------|
| deepseek-v4-pro | 2056 |
| kimi-k2.6 | 2306 |
| mistral-large-3:675b-cloud | 2396 |
| qwen3.5_cloud | 2120 |
| willis | 388 |

- **Union across all files:** 5,012
- **Intersection across all files:** 120

---

## Pairwise Shared (matchup, page, date, content_type) Counts

|  | deepseek-v4-pro | kimi-k2.6 | mistral-large-3:675b-cloud | qwen3.5_cloud | willis |
| -- | --: | --: | --: | --: | --: |
| **deepseek-v4-pro** | 2056 | 1193 | 1180 | 1070 | 169 |
| **kimi-k2.6** | 1193 | 2306 | 1198 | 1067 | 185 |
| **mistral-large-3:675b-cloud** | 1180 | 1198 | 2396 | 1156 | 172 |
| **qwen3.5_cloud** | 1070 | 1067 | 1156 | 2120 | 158 |
| **willis** | 169 | 185 | 172 | 158 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | deepseek-v4-pro | kimi-k2.6 | mistral-large-3:675b-cloud | qwen3.5_cloud | willis |
| -- | --: | --: | --: | --: | --: |
| **deepseek-v4-pro** | 1.000 | 0.376 | 0.361 | 0.344 | 0.074 |
| **kimi-k2.6** | 0.376 | 1.000 | 0.342 | 0.318 | 0.074 |
| **mistral-large-3:675b-cloud** | 0.361 | 0.342 | 1.000 | 0.344 | 0.066 |
| **qwen3.5_cloud** | 0.344 | 0.318 | 0.344 | 1.000 | 0.067 |
| **willis** | 0.074 | 0.074 | 0.066 | 0.067 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| deepseek-v4-pro vs kimi-k2.6 | 863 | 1113 |
| deepseek-v4-pro vs mistral-large-3:675b-cloud | 876 | 1216 |
| deepseek-v4-pro vs qwen3.5_cloud | 986 | 1050 |
| deepseek-v4-pro vs willis | 1887 | 219 |
| kimi-k2.6 vs mistral-large-3:675b-cloud | 1108 | 1198 |
| kimi-k2.6 vs qwen3.5_cloud | 1239 | 1053 |
| kimi-k2.6 vs willis | 2121 | 203 |
| mistral-large-3:675b-cloud vs qwen3.5_cloud | 1240 | 964 |
| mistral-large-3:675b-cloud vs willis | 2224 | 216 |
| qwen3.5_cloud vs willis | 1962 | 230 |

---

## Agreement Distribution

How many of the 7 files agree on each unique (matchup, page, date, content_type) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 5 | 3007 |
| 2 / 5 | 681 |
| 3 / 5 | 519 |
| 4 / 5 | 685 |
| 5 / 5 | 120 |
