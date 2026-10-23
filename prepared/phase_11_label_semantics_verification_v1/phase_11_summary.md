# Phase 11 Summary — Label Semantics and Independent Evaluation Source Verification

**Project:** AgriChain AI  
**Phase:** 11 — Label Semantics and Independent Evaluation Source Verification  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_11_label_semantics_verification_v1`  
**Created:** 2026-10-17  
**Status:** Read-only evidence verification. No model loaded, trained, or evaluated.

---

## 1. Objective

Determine whether the existing Healthy & Rotten / Fruit And Vegetable Diseases dataset can legitimately support an independent evaluation of AgriChain AI's frozen Fresh/Rotten models. Two questions:

1. Is there credible documentation explaining what the source labels `Healthy` and `Rotten` actually mean?
2. Do eligible candidate images overlap with previously used Fresh/Rotten training, validation, or test data?

---

## 2. Label Documentation Evidence — NOT FOUND

### Local source directory inventory

| File type | Count |
|---|---|
| Images (.jpg, .png, .jpeg, .webp) | 29,277 |
| Documentation files (README, txt, json, csv, yaml, pdf, etc.) | **0** |

The source directory contains **only images** — no README, no data dictionary, no label definitions, no provenance records, no documentation of any kind.

### Phase 04 preparation reports

Both `class_mapping.json` and `dataset_summary.md` explicitly state:

> "Source root names this a Diseases Dataset; no documentation establishes that 'Rotten' is equivalent to Freshness ground truth."

Every class entry states: "Not independently verified as food safety or shelf-life label."

### Public source

Attempted to access `https://www.kaggle.com/dsv/8463025` — no readable documentation returned.

### Label-semantics evidence questions — all unresolved

| Question | Answer |
|---|---|
| What does `Healthy` mean operationally? | Not documented |
| What does `Rotten` mean operationally? | Not documented |
| Label assignment method? | Unknown |
| Distinguishes freshness from disease/damage/ripeness? | Not established |
| Sample-level provenance documented? | No |
| Valid mapping to Fresh/Rotten classes? | Not established |

---

## 3. Overlap Check Results — All Fresh/Rotten Partitions

Exact SHA-256 overlap was checked between Phase 10 eligible candidates (17,309) and all Fresh/Rotten partitions:

| Partition | Images | Overlap with candidates | Status |
|---|---|---|---|
| Training | 7,497 | 0 | Resolved — no overlap |
| Validation | 1,876 | 0 | Resolved — no overlap |
| Old test (previously used) | 2,408 | **2,200** | **Resolved — excluded** |

After excluding the 2,200 old-test overlaps, **15,109 candidate images** are hash-independent of all Fresh/Rotten model-development and previously used test data.

### Within-candidate duplicates

0 cross-source duplicate groups within the eligible candidate set.

---

## 4. Revised Eligibility Results

| Metric | Count |
|---|---|
| Phase 10 eligible candidates | 17,309 |
| Excluded — old test partition overlap | 2,200 |
| Passing overlap/mapping/conflict checks | 15,109 |
| Label semantics verified | **0** (all UNVERIFIED) |
| **Final endorsed evaluation samples** | **0** |

### Per-class breakdown (15,109 passing overlap checks, but NOT endorsed)

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

**All 15,109 are marked `NOT_ENDORSED_unverified_label_semantics`** because label semantics cannot be verified.

---

## 5. Unresolved Labels

Five Carrot records have conflicting `Carrot__Healthy`/`Carrot__Rotten` labels on identical byte content (SHA-256: `503d881f...` and `9d575437...`). These are documented in `unresolved_labels.csv` and excluded from evaluation.

---

## 6. Final Readiness Decision

**Status: `BLOCKED`**

The available source evidence does not support defensible independent evaluation:

- **BLOCKER 1:** Label semantics UNVERIFIED — no documentation establishes Healthy/Rotten → Fresh/Rotten
- **BLOCKER 2:** 2,200 images overlap with old test partition (excluded)
- **BLOCKER 3:** No class mapping endorsed (0 of 28 classes eligible)
- **Caveat:** Exact-hash non-match does not guarantee complete independence (resized copies, recompressed images, related photographs possible)

---

## 7. What Cannot Be Claimed

- Cannot claim Healthy & Rotten labels are equivalent to Fresh/Rotten ground truth
- Cannot claim any sample is verified evaluation ground truth
- Cannot claim independent evaluation readiness
- Cannot claim production readiness for either model

---

## 8. Created Files

| File | Description |
|---|---|
| `source_evidence_report.md` | Source provenance, evidence reviewed, label methodology, limitations |
| `label_semantics_decision.json` | Per-class label semantics decisions with evidence references |
| `test_overlap_report.json` | Hash sources, per-partition overlap counts, duplicate details |
| `old_test_overlap_complete.json` | Complete 2,200-record old-test overlap data |
| `independent_eval_eligibility.csv` | 15,109 candidates passing overlap checks (NOT endorsed) |
| `excluded_candidates.csv` | 2,200 excluded samples (old-test overlap) |
| `unresolved_labels.csv` | 5 conflicting Carrot label records |
| `evaluation_protocol_draft.md` | Proposed future protocol (not executed) |
| `data_acquisition_requirements.md` | Requirements for verified label documentation or new data |
| `phase_11_summary.md` | This document |
| `README.md` | Artifact descriptions and reproducibility notes |
| `verify_phase11.py` | Reusable read-only verification script |

---

## 9. Recommended Next Step

**Obtain authoritative label semantics documentation** for the Healthy & Rotten dataset from the publisher (Kaggle dsv/8463025). Without verified label documentation, no independent evaluation can proceed. If documentation cannot be obtained, collect or acquire a new independent Fresh/Rotten evaluation dataset per `data_acquisition_requirements.md`.

**Stop after Phase 11.** Do not begin model evaluation or integration automatically.

---

## 10. Confirmation

- No models were loaded, trained, or evaluated.
- No model checkpoints were loaded.
- No inference was run.
- No accuracy, F1, or other model-performance metrics were calculated.
- No source labels, original dataset files, or split assignments were modified.
- No Phase 03–10 deliverables were modified or overwritten.
- No datasets, images, archives, or model weights were downloaded.
- No dependencies were installed or upgraded.
- No application code was modified.
