# Healthy & Rotten / Fruit And Vegetable Diseases Dataset preparation summary

- Status: **PREPARED_WITH_LIMITATIONS**
- Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\healty_&_rotten\Fruit And Vegetable Diseases Dataset`
- Decodable candidates before duplicate handling: 29291
- Accepted unique images: 27513
- Excluded records: 1773 (exact duplicates removed: 1776; cross-split duplicate groups: 0; decode failures: 0)
- Unresolved records: 5 (duplicate byte groups with conflicting labels require review).
- Classes: 28
- Extension/actual-format mismatches: 403
- Split policy: deterministic per-class 80/10/10 assignment after exact-duplicate grouping.

## Class counts by split

| Class | train | validation | test | total |
|---|---:|---:|---:|---:|
| Apple__Healthy | 1945 | 243 | 244 | 2432 |
| Apple__Rotten | 2344 | 293 | 293 | 2930 |
| Banana__Healthy | 1599 | 199 | 201 | 1999 |
| Banana__Rotten | 2234 | 279 | 280 | 2793 |
| Bellpepper__Healthy | 480 | 60 | 60 | 600 |
| Bellpepper__Rotten | 437 | 54 | 56 | 547 |
| Carrot__Healthy | 486 | 60 | 62 | 608 |
| Carrot__Rotten | 404 | 50 | 52 | 506 |
| Cucumber__Healthy | 472 | 59 | 60 | 591 |
| Cucumber__Rotten | 460 | 57 | 59 | 576 |
| Grape__Healthy | 160 | 20 | 20 | 200 |
| Grape__Rotten | 160 | 20 | 20 | 200 |
| Guava__Healthy | 160 | 20 | 20 | 200 |
| Guava__Rotten | 160 | 20 | 20 | 200 |
| Jujube__Healthy | 160 | 20 | 20 | 200 |
| Jujube__Rotten | 160 | 20 | 20 | 200 |
| Mango__Healthy | 1143 | 142 | 144 | 1429 |
| Mango__Rotten | 1411 | 176 | 177 | 1764 |
| Orange__Healthy | 1640 | 205 | 206 | 2051 |
| Orange__Rotten | 1724 | 215 | 217 | 2156 |
| Pomegranate__Healthy | 160 | 20 | 20 | 200 |
| Pomegranate__Rotten | 160 | 20 | 20 | 200 |
| Potato__Healthy | 488 | 61 | 61 | 610 |
| Potato__Rotten | 451 | 56 | 57 | 564 |
| Strawberry__Healthy | 1016 | 127 | 128 | 1271 |
| Strawberry__Rotten | 1048 | 131 | 131 | 1310 |
| Tomato__Healthy | 481 | 60 | 61 | 602 |
| Tomato__Rotten | 459 | 57 | 58 | 574 |

## Limitations

Folder taxonomy pairs 14 produce types with Healthy/Rotten labels. Source root names this a Diseases Dataset; no documentation establishes that “Rotten” is equivalent to Freshness ground truth. No official split exists; deterministic grouped 80/10/10 splits use seed 2048 after conflicting duplicate groups are held unresolved.

Counts reflect files decoded during this pass. Folder-derived labels are preserved, not adjudicated. Image decoding does not establish semantic label correctness or production readiness.
