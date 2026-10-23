# VegNet preparation summary

- Status: **PREPARED_WITH_LIMITATIONS**
- Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\vegetable_quality\vegnet\VegNet Vegetable Dataset with quality (Unripe, Ripe, Old, Dried and Damaged)\VegNet (Unripe, Ripe, Old, Dried and Damaged)\New VegNet`
- Decodable candidates: 6150
- Accepted unique images: 6150
- Excluded (including duplicates): 0
- Folder labels: 20 (19 populated; `4. Tomato/Dried` has 0 images).
- Extension/format mismatches: 0
- Deterministic class-stratified 80/10/10 split, seed 2048, after exact hash grouping.

## Class counts by split

| Produce / quality | train | validation | test | total |
|---|---:|---:|---:|---:|
| 1. Bell Pepper/Damaged | 24 | 3 | 4 | 31 |
| 1. Bell Pepper/Dried | 236 | 29 | 31 | 296 |
| 1. Bell Pepper/Old | 279 | 34 | 36 | 349 |
| 1. Bell Pepper/Ripe | 358 | 44 | 46 | 448 |
| 1. Bell Pepper/Unripe | 41 | 5 | 6 | 52 |
| 2. Chile Pepper/Damaged | 96 | 12 | 13 | 121 |
| 2. Chile Pepper/Dried | 474 | 59 | 60 | 593 |
| 2. Chile Pepper/Old | 160 | 20 | 20 | 200 |
| 2. Chile Pepper/Ripe | 146 | 18 | 19 | 183 |
| 2. Chile Pepper/Unripe | 151 | 18 | 20 | 189 |
| 3. New Mexico Green Chile/Damaged | 110 | 13 | 15 | 138 |
| 3. New Mexico Green Chile/Dried | 400 | 50 | 50 | 500 |
| 3. New Mexico Green Chile/Old | 208 | 26 | 27 | 261 |
| 3. New Mexico Green Chile/Ripe | 160 | 20 | 21 | 201 |
| 3. New Mexico Green Chile/Unripe | 181 | 22 | 24 | 227 |
| 4. Tomato/Damaged | 21 | 2 | 4 | 27 |
| 4. Tomato/Old | 987 | 123 | 124 | 1234 |
| 4. Tomato/Ripe | 764 | 95 | 96 | 955 |
| 4. Tomato/Unripe | 116 | 14 | 15 | 145 |
| 4. Tomato/Dried | 0 | 0 | 0 | 0 |

## Limitations

Tomato/Dried has no images (and therefore is absent from the observed class mapping). Class counts are imbalanced. No source documentation was found to define visual criteria for the five quality labels; folder names are retained verbatim. No image was transformed or copied.

