# Match Index Comparison Results

## Files Loaded

| File | Unique (matchup, page, date, content_type) rows |
|------|---------------------------------------------------|
| deepseek-v4-pro | 2056 |
| gemma4-31b | 1943 |
| glm-5.1 | 2104 |
| glm-5.2_cloud | 1819 |
| kimi-k2.6 | 2306 |
| minimax-m3_cloud | 170 |
| mistral-large-3:675b-cloud | 2396 |
| qwen3.5_397b-cloud | 2206 |
| qwen3.5_397b-cloud_fixed | 2177 |
| qwen3.5_cloud | 2120 |
| willis | 388 |

- **Union across all files:** 7,065
- **Intersection across all files:** 54

---

## Pairwise Shared (matchup, page, date, content_type) Counts

|  | deepseek-v4-pro | gemma4-31b | glm-5.1 | glm-5.2_cloud | kimi-k2.6 | minimax-m3_cloud | mistral-large-3:675b-cloud | qwen3.5_397b-cloud | qwen3.5_397b-cloud_fixed | qwen3.5_cloud | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **deepseek-v4-pro** | 2056 | 1072 | 1189 | 1128 | 1195 | 108 | 1183 | 1043 | 1010 | 1071 | 170 |
| **gemma4-31b** | 1072 | 1943 | 1107 | 1150 | 1075 | 129 | 1082 | 1032 | 1048 | 1002 | 186 |
| **glm-5.1** | 1189 | 1107 | 2104 | 1173 | 1171 | 112 | 1238 | 1025 | 1020 | 1089 | 195 |
| **glm-5.2_cloud** | 1128 | 1150 | 1173 | 1819 | 1097 | 123 | 1134 | 1029 | 1035 | 1024 | 194 |
| **kimi-k2.6** | 1195 | 1075 | 1171 | 1097 | 2306 | 114 | 1199 | 1036 | 1003 | 1067 | 185 |
| **minimax-m3_cloud** | 108 | 129 | 112 | 123 | 114 | 170 | 111 | 101 | 107 | 99 | 86 |
| **mistral-large-3:675b-cloud** | 1183 | 1082 | 1238 | 1134 | 1199 | 111 | 2396 | 1071 | 1049 | 1156 | 172 |
| **qwen3.5_397b-cloud** | 1043 | 1032 | 1025 | 1029 | 1036 | 101 | 1071 | 2206 | 1502 | 1312 | 155 |
| **qwen3.5_397b-cloud_fixed** | 1010 | 1048 | 1020 | 1035 | 1003 | 107 | 1049 | 1502 | 2177 | 1302 | 153 |
| **qwen3.5_cloud** | 1071 | 1002 | 1089 | 1024 | 1067 | 99 | 1156 | 1312 | 1302 | 2120 | 158 |
| **willis** | 170 | 186 | 195 | 194 | 185 | 86 | 172 | 155 | 153 | 158 | 388 |

---

## Pairwise Jaccard Similarity (|A∩B| / |A∪B|)

|  | deepseek-v4-pro | gemma4-31b | glm-5.1 | glm-5.2_cloud | kimi-k2.6 | minimax-m3_cloud | mistral-large-3:675b-cloud | qwen3.5_397b-cloud | qwen3.5_397b-cloud_fixed | qwen3.5_cloud | willis |
| -- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **deepseek-v4-pro** | 1.000 | 0.366 | 0.400 | 0.411 | 0.377 | 0.051 | 0.362 | 0.324 | 0.313 | 0.345 | 0.075 |
| **gemma4-31b** | 0.366 | 1.000 | 0.377 | 0.440 | 0.339 | 0.065 | 0.332 | 0.331 | 0.341 | 0.327 | 0.087 |
| **glm-5.1** | 0.400 | 0.377 | 1.000 | 0.427 | 0.362 | 0.052 | 0.380 | 0.312 | 0.313 | 0.347 | 0.085 |
| **glm-5.2_cloud** | 0.411 | 0.440 | 0.427 | 1.000 | 0.362 | 0.066 | 0.368 | 0.343 | 0.350 | 0.351 | 0.096 |
| **kimi-k2.6** | 0.377 | 0.339 | 0.362 | 0.362 | 1.000 | 0.048 | 0.342 | 0.298 | 0.288 | 0.318 | 0.074 |
| **minimax-m3_cloud** | 0.051 | 0.065 | 0.052 | 0.066 | 0.048 | 1.000 | 0.045 | 0.044 | 0.048 | 0.045 | 0.182 |
| **mistral-large-3:675b-cloud** | 0.362 | 0.332 | 0.380 | 0.368 | 0.342 | 0.045 | 1.000 | 0.303 | 0.298 | 0.344 | 0.066 |
| **qwen3.5_397b-cloud** | 0.324 | 0.331 | 0.312 | 0.343 | 0.298 | 0.044 | 0.303 | 1.000 | 0.521 | 0.435 | 0.064 |
| **qwen3.5_397b-cloud_fixed** | 0.313 | 0.341 | 0.313 | 0.350 | 0.288 | 0.048 | 0.298 | 0.521 | 1.000 | 0.435 | 0.063 |
| **qwen3.5_cloud** | 0.345 | 0.327 | 0.347 | 0.351 | 0.318 | 0.045 | 0.344 | 0.435 | 0.435 | 1.000 | 0.067 |
| **willis** | 0.075 | 0.087 | 0.085 | 0.096 | 0.074 | 0.182 | 0.066 | 0.064 | 0.063 | 0.067 | 1.000 |

---

## Pair Disagreements

Rows present in one file but not the other:

| Pair | Only in A | Only in B |
|------|----------:|----------:|
| deepseek-v4-pro vs gemma4-31b | 984 | 871 |
| deepseek-v4-pro vs glm-5.1 | 867 | 915 |
| deepseek-v4-pro vs glm-5.2_cloud | 928 | 691 |
| deepseek-v4-pro vs kimi-k2.6 | 861 | 1111 |
| deepseek-v4-pro vs minimax-m3_cloud | 1948 | 62 |
| deepseek-v4-pro vs mistral-large-3:675b-cloud | 873 | 1213 |
| deepseek-v4-pro vs qwen3.5_397b-cloud | 1013 | 1163 |
| deepseek-v4-pro vs qwen3.5_397b-cloud_fixed | 1046 | 1167 |
| deepseek-v4-pro vs qwen3.5_cloud | 985 | 1049 |
| deepseek-v4-pro vs willis | 1886 | 218 |
| gemma4-31b vs glm-5.1 | 836 | 997 |
| gemma4-31b vs glm-5.2_cloud | 793 | 669 |
| gemma4-31b vs kimi-k2.6 | 868 | 1231 |
| gemma4-31b vs minimax-m3_cloud | 1814 | 41 |
| gemma4-31b vs mistral-large-3:675b-cloud | 861 | 1314 |
| gemma4-31b vs qwen3.5_397b-cloud | 911 | 1174 |
| gemma4-31b vs qwen3.5_397b-cloud_fixed | 895 | 1129 |
| gemma4-31b vs qwen3.5_cloud | 941 | 1118 |
| gemma4-31b vs willis | 1757 | 202 |
| glm-5.1 vs glm-5.2_cloud | 931 | 646 |
| glm-5.1 vs kimi-k2.6 | 933 | 1135 |
| glm-5.1 vs minimax-m3_cloud | 1992 | 58 |
| glm-5.1 vs mistral-large-3:675b-cloud | 866 | 1158 |
| glm-5.1 vs qwen3.5_397b-cloud | 1079 | 1181 |
| glm-5.1 vs qwen3.5_397b-cloud_fixed | 1084 | 1157 |
| glm-5.1 vs qwen3.5_cloud | 1015 | 1031 |
| glm-5.1 vs willis | 1909 | 193 |
| glm-5.2_cloud vs kimi-k2.6 | 722 | 1209 |
| glm-5.2_cloud vs minimax-m3_cloud | 1696 | 47 |
| glm-5.2_cloud vs mistral-large-3:675b-cloud | 685 | 1262 |
| glm-5.2_cloud vs qwen3.5_397b-cloud | 790 | 1177 |
| glm-5.2_cloud vs qwen3.5_397b-cloud_fixed | 784 | 1142 |
| glm-5.2_cloud vs qwen3.5_cloud | 795 | 1096 |
| glm-5.2_cloud vs willis | 1625 | 194 |
| kimi-k2.6 vs minimax-m3_cloud | 2192 | 56 |
| kimi-k2.6 vs mistral-large-3:675b-cloud | 1107 | 1197 |
| kimi-k2.6 vs qwen3.5_397b-cloud | 1270 | 1170 |
| kimi-k2.6 vs qwen3.5_397b-cloud_fixed | 1303 | 1174 |
| kimi-k2.6 vs qwen3.5_cloud | 1239 | 1053 |
| kimi-k2.6 vs willis | 2121 | 203 |
| minimax-m3_cloud vs mistral-large-3:675b-cloud | 59 | 2285 |
| minimax-m3_cloud vs qwen3.5_397b-cloud | 69 | 2105 |
| minimax-m3_cloud vs qwen3.5_397b-cloud_fixed | 63 | 2070 |
| minimax-m3_cloud vs qwen3.5_cloud | 71 | 2021 |
| minimax-m3_cloud vs willis | 84 | 302 |
| mistral-large-3:675b-cloud vs qwen3.5_397b-cloud | 1325 | 1135 |
| mistral-large-3:675b-cloud vs qwen3.5_397b-cloud_fixed | 1347 | 1128 |
| mistral-large-3:675b-cloud vs qwen3.5_cloud | 1240 | 964 |
| mistral-large-3:675b-cloud vs willis | 2224 | 216 |
| qwen3.5_397b-cloud vs qwen3.5_397b-cloud_fixed | 704 | 675 |
| qwen3.5_397b-cloud vs qwen3.5_cloud | 894 | 808 |
| qwen3.5_397b-cloud vs willis | 2051 | 233 |
| qwen3.5_397b-cloud_fixed vs qwen3.5_cloud | 875 | 818 |
| qwen3.5_397b-cloud_fixed vs willis | 2024 | 235 |
| qwen3.5_cloud vs willis | 1962 | 230 |

---

## Agreement Distribution

How many of the 11 files agree on each unique (matchup, page, date, content_type) key:

| Files agreeing | Count of keys |
|---------------:|--------------:|
| 1 / 11 | 3714 |
| 2 / 11 | 1028 |
| 3 / 11 | 554 |
| 4 / 11 | 299 |
| 5 / 11 | 281 |
| 6 / 11 | 216 |
| 7 / 11 | 187 |
| 8 / 11 | 209 |
| 9 / 11 | 449 |
| 10 / 11 | 74 |
| 11 / 11 | 54 |
