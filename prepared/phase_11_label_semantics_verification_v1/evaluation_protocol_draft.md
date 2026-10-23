# Phase 11 — Draft Independent Evaluation Protocol (Fresh/Rotten)

**Project:** AgriChain AI  
**Phase:** 11 — Label Semantics and Independent Evaluation Source Verification  
**Status:** DRAFT — for protocol review only. Not executed.  
**Intended use:** Future independent evaluation of the frozen Fresh/Rotten baseline and aspect-preserving candidate models, IF label semantics are first verified.

---

## 1. Purpose

Establish a genuinely independent evaluation protocol for the Fresh/Rotten models, using evaluation data that was **not** used in model development (training or validation) and was **not** previously used for baseline evaluation or error analysis.

The Phase 09 diagnostic evaluation used the existing 2,408-image test partition, which had already been used for baseline evaluation. That partition is diagnostic, not independent.

---

## 2. Preconditions (ALL Must Be Met Before Evaluation)

The following preconditions are **not yet satisfied**. The protocol cannot be executed until all are resolved:

### 2.1 Label semantics verification (BLOCKER — NOT SATISFIED)

The Healthy & Rotten source is named a "Diseases Dataset." **No documentation was found** establishing that:
- "Healthy" = "Fresh"
- "Rotten" = freshness/rotten ground truth
- Labels distinguish freshness/spoilage from disease, damage, ripeness, or appearance

The source directory contains only images — zero documentation files (no README, no data dictionary, no label definitions). Phase 04 reports explicitly state: "no documentation establishes that 'Rotten' is equivalent to Freshness ground truth."

**Required:** Obtain authoritative documentation (data dictionary, label-generation protocol) from the dataset publisher verifying label semantics. Without this, no sample can be used as verified ground truth.

### 2.2 Independence from model-development data (PARTIALLY SATISFIED)

Exact-duplicate (SHA-256) overlap was checked against all Fresh/Rotten partitions:

| Partition | Overlap with eligible candidates | Status |
|---|---|---|
| Training (7,497 images) | 0 | Resolved — no overlap |
| Validation (1,876 images) | 0 | Resolved — no overlap |
| Old test partition (2,408 images) | 2,200 | **Resolved — excluded from eligible set** |

After excluding the 2,200 old-test overlaps, 15,109 candidate images are hash-independent of all Fresh/Rotten model-development and previously used test data.

**Caveat:** Exact-hash non-match does not guarantee complete independence. Resized copies, recompressed images, related photographs, and shared source collections may remain possible. Provenance/collection-session grouping is not documented.

### 2.3 Class coverage

Only 10 of the Healthy & Rotten dataset's 14 produce types map to the Fresh/Rotten model's 20 classes. Grape, Guava, Jujube, and Pomegranate (1,600 images in Phase 10) are excluded because they have no corresponding class in the model.

### 2.4 Conflicting labels

Five Carrot records have conflicting `Carrot__Healthy`/`Carrot__Rotten` labels on identical byte content. These are excluded from the eligible set.

### 2.5 Class balance

After all exclusions, 15,109 images pass overlap/mapping/conflict checks, but class distribution is imbalanced (110 to 2,624 per class). Priority classes (RottenBellpepper, RottenCarrot, RottenTomato, RottenPotato) have only 110-118 samples each.

---

## 3. Proposed Evaluation Procedure (When All Preconditions Are Met)

1. **Label semantics:** Verify Healthy/Rotten → Fresh/Rotten mapping with authoritative documentation. Only then may any sample be considered verified ground truth.
2. **Dataset:** Use the 15,109 images from `independent_eval_eligibility.csv` that pass overlap/mapping/conflict checks, or a stratified subset thereof.
3. **Models:** Evaluate both the frozen baseline checkpoint and the frozen aspect-preserving candidate checkpoint.
4. **Preprocessing:** Use each model's own verified preprocessing. Do not substitute between models.
5. **Metrics:** Accuracy, macro-F1, balanced accuracy, per-class precision/recall/F1/support, confusion matrix, misclassification count and percentage.
6. **Metric differences:** Report in percentage points.
7. **Class order:** Use the verified 20-class mapping (FreshApple=0 through RottenTomato=19).
8. **Runtime:** CPU execution, `model.eval()`, `torch.inference_mode()`.
9. **No model modification:** No training, fine-tuning, or checkpoint modification.
10. **No test reuse:** Do not use any image from this independent set in training, validation, or model selection.
11. **Hash verification:** Record SHA-256 hashes of checkpoints, class mappings, and configs before and after evaluation.

---

## 4. What This Protocol Does NOT Do

- Does not train or fine-tune any model.
- Does not load model checkpoints or run inference (this is a draft protocol only).
- Does not calculate accuracy, F1, or any model-evaluation metrics.
- Does not touch the old 2,408-image test partition.
- Does not modify any source labels, mappings, or manifests.
- Does not claim independent evaluation readiness without adequate label and overlap evidence.

---

## 5. Required Reviews Before Execution

1. **Label semantics review:** Verify Healthy/Rotten → Fresh/Rotten mapping with authoritative documentation. **This is the primary blocker.**
2. **Protocol review:** Review and approve this draft protocol before the evaluation phase.
3. **Acceptance thresholds:** Define pre-registered acceptance thresholds before any model comparison.

---

## 6. Related Artifacts

- `source_evidence_report.md` — source provenance and evidence review
- `label_semantics_decision.json` — per-class label semantics decisions
- `test_overlap_report.json` — hash overlap findings
- `old_test_overlap_complete.json` — complete 2,200-record old-test overlap data
- `independent_eval_eligibility.csv` — 15,109 candidates passing overlap checks (NOT endorsed due to unverified label semantics)
- `excluded_candidates.csv` — 2,200 excluded samples (old-test overlap)
- `unresolved_labels.csv` — 5 conflicting Carrot label records
- `data_acquisition_requirements.md` — requirements for obtaining verified label documentation or new data
