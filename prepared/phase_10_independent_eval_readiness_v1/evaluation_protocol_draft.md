# Phase 10 — Draft Independent Evaluation Protocol (Fresh/Rotten)

**Project:** AgriChain AI  
**Phase:** 10 — Independent Fresh/Rotten Evaluation Dataset Readiness  
**Status:** DRAFT — for protocol review only. Not executed.  
**Intended use:** Future independent evaluation of the frozen Fresh/Rotten baseline and aspect-preserving candidate models.

---

## 1. Purpose

Establish a genuinely independent evaluation protocol for the Fresh/Rotten baseline and aspect-preserving candidate models, using evaluation data that was **not** used in model development (training or validation) and was **not** previously used for baseline evaluation or error analysis.

The Phase 09 diagnostic evaluation used the existing 2,408-image test partition, which had already been used for baseline evaluation. That partition is diagnostic, not independent. This draft protocol defines how a future independent evaluation should be conducted once a verified independent dataset is available.

---

## 2. Candidate Evaluation Source

**Healthy & Rotten / Fruit And Vegetable Diseases Dataset**  
Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\healty_&_rotten\Fruit And Vegetable Diseases Dataset`

### Eligible samples (preliminary)

From the Phase 10 eligibility analysis (`eligibility_analysis.json`):

| Metric | Count |
|---|---|
| Total Healthy & Rotten accepted images | 27,513 |
| Eligible for independent evaluation (mappable, no FR train/val overlap) | 17,309 |
| Excluded — overlap with FR train/val | 8,604 |
| Excluded — unmapped produce types (Grape, Guava, Jujube, Pomegranate) | 1,600 |
| Excluded — unresolved label conflicts | 0 (already excluded from manifest) |

Eligible images map to all 20 Fresh/Rotten model classes:
- FreshApple: 2,004 | RottenApple: 2,624
- FreshBanana: 1,663 | RottenBanana: 2,440
- FreshBellpepper: 122 | RottenBellpepper: 116
- FreshCarrot: 124 | RottenCarrot: 110
- FreshCucumber: 123 | RottenCucumber: 118
- FreshMango: 945 | RottenMango: 1,290
- FreshOrange: 1,721 | RottenOrange: 1,783
- FreshPotato: 123 | RottenPotato: 116
- FreshStrawberry: 815 | RottenStrawberry: 835
- FreshTomato: 121 | RottenTomato: 116

### Manifest

Eligible samples are listed in `independent_eval_manifest.csv` (17,309 records). Each record references the original image without copying it, with source path, original label, mapped Fresh/Rotten class, sha256, and eligibility decision.

---

## 3. Preconditions (Must Be Met Before Evaluation)

The following preconditions are **not yet satisfied**. The protocol cannot be executed until they are resolved:

### 3.1 Label semantics verification (BLOCKER)

The Healthy & Rotten source is named a "Diseases Dataset." Available documentation does **not** establish that:
- "Healthy" is equivalent to "Fresh"
- "Rotten" is equivalent to freshness/rotten ground truth

Before using this dataset for Fresh/Rotten evaluation, obtain authoritative documentation or a data dictionary that verifies the label semantics. Without this verification, the mapping from Healthy/Rotten to Fresh/Rotten is proposed, not verified.

### 3.2 Independence from model-development data (PARTIALLY RESOLVED)

- **Resolved:** Exact-duplicate (sha256) overlap with Fresh/Rotten training (7,497 images) and validation (1,876 images) has been checked. 8,604 overlapping images were excluded from the eligible manifest.
- **Not resolved:** Overlap with the old 2,408-image test partition could **not** be checked, because the restriction prohibits opening, copying, hashing, or processing that partition in this phase. This must be verified before the eligible images can be considered fully independent.

### 3.3 Class coverage

Only 10 of the Healthy & Rotten dataset's 14 produce types map to the Fresh/Rotten model's 20 classes. Grape, Guava, Jujube, and Pomegranate (1,600 images) are excluded because they have no corresponding class in the model.

### 3.4 Class balance

The eligible set has significant class imbalance (110 to 2,624 images per class). The evaluation protocol should account for this, particularly for the priority classes identified in Phase 09 (RottenBellpepper, RottenCarrot, RottenTomato, RottenPotato), which have relatively small eligible samples (110-118 each).

---

## 4. Proposed Evaluation Procedure (When Preconditions Are Met)

1. **Dataset:** Use the eligible samples from `independent_eval_manifest.csv` (17,309 images), or a stratified subset thereof.
2. **Models:** Evaluate both the frozen baseline checkpoint and the frozen aspect-preserving candidate checkpoint.
3. **Preprocessing:** Use each model's own verified preprocessing (baseline: direct stretch to 96x96; candidate: aspect-preserving fit + center-pad). Do not substitute preprocessing between models.
4. **Metrics:** Accuracy, macro-F1, balanced accuracy, per-class precision/recall/F1/support, confusion matrix, misclassification count and percentage.
5. **Metric differences:** Report in percentage points. Do not confuse with relative percentage improvements.
6. **Class order:** Use the verified 20-class mapping (FreshApple=0 through RottenTomato=19).
7. **Runtime:** CPU execution, `model.eval()`, `torch.inference_mode()`.
8. **No model modification:** No training, fine-tuning, or checkpoint modification.
9. **No test reuse:** Do not use any image from this independent set in training, validation, or model selection.
10. **Hash verification:** Record SHA-256 hashes of checkpoints, class mappings, and configs before and after evaluation; verify they are unchanged.

---

## 5. What This Protocol Does NOT Do

- Does not train or fine-tune any model.
- Does not load model checkpoints or run inference (this is a draft protocol only).
- Does not calculate accuracy, F1, or any model-evaluation metrics.
- Does not touch the old 2,408-image test partition.
- Does not modify any source labels, mappings, or manifests.
- Does not claim independent evaluation readiness without evidence of appropriate labels and separation from model-development data.

---

## 6. Required Reviews Before Execution

1. **Label semantics review:** Verify Healthy/Rotten → Fresh/Rotten mapping with authoritative documentation.
2. **Independence review:** Verify no overlap with the old 2,408-image test partition (once restriction is lifted).
3. **Protocol review:** Review and approve this draft protocol before the evaluation phase.
4. **Acceptance thresholds:** Define pre-registered acceptance thresholds before any model comparison.

---

## 7. Related Artifacts

- `source_candidate_registry.csv` — all source datasets considered
- `independent_eval_manifest.csv` — 17,309 eligible candidate samples
- `excluded_candidates.csv` — 10,204 excluded samples with reasons
- `unresolved_labels.csv` — 5 conflicting Carrot label records
- `overlap_report.json` — exact-duplicate overlap findings
- `eligibility_analysis.json` — detailed eligibility breakdown
- `data_acquisition_requirements.md` — requirements if no adequate source exists
