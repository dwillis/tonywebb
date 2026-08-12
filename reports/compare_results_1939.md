# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date, content_type) rows |
|------|---------------------------------------------------|
| deepseek-v4-flash_cloud_1939 | 747 |
| glm-5.2_cloud_1939 | 586 |
| nemotron-3-ultra_cloud_1939 | 673 |

- **Union across all files:** 1,180
- **Intersection across all files:** 283

---

## Pairwise Shared (matchup, page, date, content_type) Counts

|  | deepseek-v4-flash_cloud_1939 | glm-5.2_cloud_1939 | nemotron-3-ultra_cloud_1939 |
| -- | --: | --: | --: |
| **deepseek-v4-flash_cloud_1939** | 747 | 359 | 406 |
| **glm-5.2_cloud_1939** | 359 | 586 | 344 |
| **nemotron-3-ultra_cloud_1939** | 406 | 344 | 673 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | deepseek-v4-flash_cloud_1939 | glm-5.2_cloud_1939 | nemotron-3-ultra_cloud_1939 |
| -- | --: | --: | --: |
| **deepseek-v4-flash_cloud_1939** | 1.000 | 0.369 | 0.400 |
| **glm-5.2_cloud_1939** | 0.369 | 1.000 | 0.376 |
| **nemotron-3-ultra_cloud_1939** | 0.400 | 0.376 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| deepseek-v4-flash_cloud_1939 vs glm-5.2_cloud_1939 | 388 | 227 |
| deepseek-v4-flash_cloud_1939 vs nemotron-3-ultra_cloud_1939 | 341 | 267 |
| glm-5.2_cloud_1939 vs nemotron-3-ultra_cloud_1939 | 242 | 329 |

---

## Agreement Distribution

How many of the 3 files agree on each unique (matchup, page, date, content_type) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 3 | 637 |
| 2 / 3 | 260 |
| 3 / 3 | 283 |
