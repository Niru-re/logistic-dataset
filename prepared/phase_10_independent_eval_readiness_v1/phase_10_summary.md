# Phase 10 Summary — Independent Fresh/Rotten Evaluation Dataset Readiness

**Project:** AgriChain AI  
**Phase:** 10 — Independent Fresh/Rotten Evaluation Dataset Readiness  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_10_independent_eval_readiness_v1`  
**Created:** 2026-10-17  
**Status:** Read-only audit and reporting. No model inference, training, or metric calculation performed.

---

## 1. Objective

Determine whether the project already contains a suitable, distinct source dataset for a future independent Fresh/Rotten evaluation of the frozen baseline and aspect-preserving candidate models. The Phase 09 diagnostic evaluation used the old 2,408-image test partition, which had already been used for baseline evaluation — it is not an independent test set.

---

## 2. Source Datasets Considered

All dataset families from Phase 08 were evaluated for suitability as an independent Fresh/Rotten evaluation source:

| Source Dataset | Considered? | Actual Images | Eligible Images | Readiness Status |
|---|---|---|---|---|
| Healthy & Rotten / Fruit And Vegetable Diseases | Yes | 27,513 | 17,309 | PREPARED_WITH_LIMITATIONS |
| Fruits-360 | No (variety, not freshness) | 190,873 | 0 | NOT_FOUND |
| VegNet | No (quality states, no verified Fresh/Rotten mapping) | 6,150 | 0 | NOT_FOUND |
| Fruits & Vegetables Detection Dataset | No (object detection, BLOCKED) | 180 | 0 | BLOCKED |
| Door Open/Close YOLO | No (not produce freshness) | 706 | 0 | NOT_FOUND |
| Mango Cold-Chain Measurements | No (tabular, not images) | 563 files | 0 | NOT_FOUND |
| Food Expiry CSV | No (tabular, BLOCKED) | 200,000 rows | 0 | BLOCKED |
| Dynamic Logistics CSV | No (tabular, BLOCKED) | 32,065 rows | 0 | BLOCKED |
| Fish / Seafood Dataset | No (NOT_FOUND) | 0 | 0 | NOT_FOUND |

**Only one source was considered viable:** Healthy & Rotten / Fruit And Vegetable Diseases Dataset.

---

## 3. Healthy & Rotten Dataset — Eligibility Analysis

### Source details
- **Source:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\healty_&_rotten\Fruit And Vegetable Diseases Dataset`
- **Total accepted images:** 27,513
- **Classes:** 28 (14 produce types × Healthy/Rotten)
- **Produce types overlapping with Fresh/Rotten model:** 10 (Apple, Banana, Bellpepper, Carrot, Cucumber, Mango, Orange, Potato, Strawberry, Tomato)
- **Produce types NOT in Fresh/Rotten model:** 4 (Grape, Guava, Jujube, Pomegranate) — 1,600 images excluded

### Overlap check with model-development data

Exact-duplicate (sha256) overlap was checked against Fresh/Rotten training (7,497 images) and validation (1,876 images) partitions only. The old 2,408-image test partition was **not** checked (restricted).

| Check | Result |
|---|---|
| HR images overlapping FR train/val | 8,604 (excluded from eligible set) |
| HR images with no FR train/val overlap | 18,909 |
| Of those, in mappable produce types | 17,309 (eligible) |
| Of those, in unmapped produce types | 1,600 (excluded) |
| Unresolved conflict records in manifest | 0 (already excluded) |

### Eligible images by mapped Fresh/Rotten class

| Class | Count | Class | Count |
|---|---|---|---|
| FreshApple | 2,004 | RottenApple | 2,624 |
| FreshBanana | 1,663 | RottenBanana | 2,440 |
| FreshBellpepper | 122 | RottenBellpepper | 116 |
| FreshCarrot | 124 | RottenCarrot | 110 |
| FreshCucumber | 123 | RottenCucumber | 118 |
| FreshMango | 945 | RottenMango | 1,290 |
| FreshOrange | 1,721 | RottenOrange | 1,783 |
| FreshPotato | 123 | RottenPotato | 116 |
| FreshStrawberry | 815 | RottenStrawberry | 835 |
| FreshTomato | 121 | RottenTomato | 116 |

**Total eligible: 17,309 images across all 20 Fresh/Rotten classes.**

---

## 4. Critical Limitations (Blockers)

### Blocker 1: Label semantics not verified

The Healthy & Rotten source is named a "Diseases Dataset." Available documentation explicitly states:
> "Source root names this a Diseases Dataset; no documentation establishes that 'Rotten' is equivalent to Freshness ground truth."

The mapping from Healthy/Rotten to Fresh/Rotten is **proposed, not verified**. Without authoritative documentation, these labels cannot be defensibly used as Fresh/Rotten ground truth.

### Blocker 2: Independence not fully established

- **Resolved:** No exact-duplicate overlap with Fresh/Rotten training (7,497) or validation (1,876) images. 8,604 overlapping images excluded.
- **Not resolved:** Overlap with the old 2,408-image test partition could **not** be checked. This phase is restricted from opening, copying, hashing, or processing that partition.

### Blocker 3: Class imbalance

Eligible samples range from 110 to 2,624 per class. Priority classes identified in Phase 09 (RottenBellpepper: 116, RottenCarrot: 110, RottenTomato: 116, RottenPotato: 116) have relatively small samples, limiting per-class metric reliability.

---

## 5. Final Readiness Status

**Status: `PREPARED_WITH_LIMITATIONS`**

Candidate samples exist (17,309 eligible images across all 20 Fresh/Rotten classes), but meaningful limitations remain:

1. Label semantics unverified (Healthy/Rotten ≠ verified Fresh/Rotten)
2. Independence from old test partition not checked (restricted)
3. Class imbalance, especially for priority Rotten classes

This status does **not** authorize immediate model acceptance. A frozen evaluation protocol must be reviewed and the limitations resolved before the later evaluation phase.

---

## 6. What Cannot Be Claimed

- Cannot claim Healthy & Rotten labels are equivalent to Fresh/Rotten ground truth
- Cannot claim full independence from model-development data (old test partition overlap unknown)
- Cannot claim the eligible set is ready for immediate evaluation without protocol review
- Cannot claim production readiness for either model based on this analysis

---

## 7. Created Files

| File | Description |
|---|---|
| `source_candidate_registry.csv` | All source datasets considered and their suitability |
| `independent_eval_manifest.csv` | 17,309 eligible candidate samples (references original images only) |
| `excluded_candidates.csv` | 10,204 excluded samples with reasons |
| `unresolved_labels.csv` | 5 conflicting Carrot label records |
| `overlap_report.json` | Exact-duplicate overlap findings with FR train/val |
| `eligibility_analysis.json` | Detailed eligibility breakdown |
| `evaluation_protocol_draft.md` | Proposed future evaluation protocol (not executed) |
| `data_acquisition_requirements.md` | Requirements if no adequate existing source |
| `phase_10_summary.md` | This document |
| `README.md` | Artifact descriptions and reproducibility notes |
| `verify_phase10.py` | Reusable read-only verification script |

---

## 8. Recommended Next Step

**Pursue label semantics verification for the Healthy & Rotten dataset.** Request or obtain authoritative documentation (data dictionary, label-generation protocol) that verifies whether "Healthy" = "Fresh" and "Rotten" = freshness ground truth. If verified, and once overlap with the old test partition is confirmed absent, finalize the independent evaluation protocol and proceed to the evaluation phase. If not verified, collect or acquire a new independent Fresh/Rotten evaluation dataset per `data_acquisition_requirements.md`.

Stop after Phase 10. Do not begin model evaluation automatically.
