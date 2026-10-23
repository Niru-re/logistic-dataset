# Phase 09 Summary — Fresh/Rotten Candidate Diagnostic Evaluation

**Project:** AgriChain AI  
**Phase:** 09 — Fresh/Rotten Candidate Diagnostic Evaluation  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\trained_models\fresh_rotten_v1\phase_09_candidate_diagnostic_evaluation_v1`  
**Created:** 2026-10-17  
**Status:** Read-only diagnostic evaluation. No training, fine-tuning, or model modification.

---

## 1. What Was Done

Evaluated the existing **baseline** and **aspect-preserving candidate** Fresh/Rotten checkpoints against the same existing 2,408-image test partition in one controlled run. Both models used their own verified preprocessing (baseline: direct stretch to 96x96; candidate: aspect-preserving fit + center-pad). The same 20-class mapping, metric definitions, CPU execution, `model.eval()`, and `torch.inference_mode()` were used for both.

This is a **comparative diagnostic evaluation**, not an independent final acceptance test. The test partition was previously used for baseline evaluation (Phase 02). The candidate had not previously been evaluated on this partition.

---

## 2. Test Partition

| Attribute | Value |
|---|---|
| Assigned test images | 2,408 |
| Evaluated (baseline) | 2,408 |
| Evaluated (candidate) | 2,408 |
| Failures (baseline) | 0 |
| Failures (candidate) | 0 |
| Source manifest | `datasets/prepared/fresh_rotten_v1/dataset_manifest.csv` (assigned_split == "test") |
| Class count | 20 |
| Decode errors | 0 |

All 2,408 test images were successfully processed by both models. No images failed to load or process. No train or validation images were used in test metrics.

---

## 3. Results

### Baseline (reproduced, compared against historical reference)

| Metric | This phase (reproduced) | Historical reference (Phase 02) | Match? |
|---|---|---|---|
| Accuracy | 79.73% | 79.73% | Yes |
| Macro-F1 | 79.81% | 79.81% | Yes |
| Balanced accuracy | 79.63% | 79.63% | Yes |
| Misclassified | 488 / 2,408 | 488 / 2,408 | Yes |

The newly reproduced baseline matches the historical Phase 02 report exactly, validating the evaluation methodology, class order, preprocessing, and metric definitions.

### Candidate (first time on held-out test partition)

| Metric | Value |
|---|---|
| Accuracy | 83.51% |
| Macro-F1 | 83.65% |
| Balanced accuracy | 83.44% |
| Misclassified | 397 / 2,408 |

### Difference (candidate minus baseline, percentage points)

| Metric | Difference |
|---|---|
| Accuracy | +3.78 pp |
| Macro-F1 | +3.85 pp |
| Balanced accuracy | +3.81 pp |
| Misclassified | 488 → 397 (91 fewer errors) |

### Candidate vs its own validation (reference only, not test)

| Metric | Candidate validation (Phase 02) | Candidate test (this phase) |
|---|---|---|
| Macro-F1 | 84.04% | 83.65% |
| Balanced accuracy | 83.93% | 83.44% |

Validation metrics remain clearly separated from test metrics. The candidate's test macro-F1 (83.65%) is slightly below its validation macro-F1 (84.04%), which is expected and not a discrepancy.

---

## 4. Priority Class Results

Four priority Rotten classes were examined individually:

| Class | Support | Baseline F1 | Candidate F1 | Diff (pp) | Baseline Recall | Candidate Recall |
|---|---|---|---|---|---|---|
| RottenBellpepper | 119 | 0.4878 | 0.5420 | +5.42 | 0.5042 | 0.5966 |
| RottenCarrot | 116 | 0.7005 | 0.6964 | **−0.40** | 0.6552 | 0.6724 |
| RottenTomato | 120 | 0.6389 | 0.7054 | +6.65 | 0.5750 | 0.6583 |
| RottenPotato | 117 | 0.6128 | 0.7063 | +9.35 | 0.7778 | 0.8632 |

**Priority Rotten mean F1:** baseline 0.6100 → candidate 0.6625 (+5.25 pp)

**Important observation:** Three of the four priority classes improved (RottenBellpepper +5.42 pp, RottenTomato +6.65 pp, RottenPotato +9.35 pp). However, **RottenCarrot F1 decreased slightly (−0.40 pp)** despite a small recall gain, because precision dropped more (0.7525 → 0.7222). This mixed behavior means the candidate is not uniformly better across all priority classes.

---

## 5. Artifact Integrity

SHA-256 hashes of the baseline checkpoint, candidate checkpoint, class mappings, training configs, training scripts, and dataset manifest were recorded before evaluation and verified after. **All hashes remained unchanged.** No source artifacts were modified.

- Baseline checkpoint SHA-256: `82dd2d1784b794187665aaeb2ac340deee8b1b530c8cb5981d7ec22214960049` (matches Phase 02 record)
- Dataset manifest SHA-256: `4a5c1fc7628335b15ffc37b31327934121142701cfe78c4817b3f69293eefbfc` (matches Phase 02 record)

---

## 6. Limitations

- **Diagnostic, not independent:** The test partition was previously used for baseline evaluation and error analysis. Results are comparative evidence, not independent acceptance.
- **Previously used test set:** Because the baseline was already evaluated on this partition, the test set is not untouched. A fresh, independently collected or adjudicated evaluation set is still required before any acceptance decision.
- **Labels are folder-derived:** Dataset provenance and capture conditions are not independently established.
- **CPU-only, 2 Torch threads:** No GPU/CUDA available. PyTorch 2.2.1+cpu with NumPy 2.2.6 emits an ABI warning; inference avoids the NumPy bridge (consistent with prior phases).
- **Softmax scores are uncalibrated:** They are not food-safety, shelf-life, freshness-certification, or shipment-survival estimates.
- **No new acceptance threshold:** No pre-existing acceptance thresholds were documented; no acceptance conclusion is inferred from these metrics.
- **RottenCarrot mixed result:** The candidate's F1 on RottenCarrot decreased slightly (−0.40 pp), so improvement is not uniform across priority classes.

---

## 7. Created Files

| File | Description |
|---|---|
| `evaluation_protocol.md` | Frozen protocol and limitations |
| `evaluation_config.json` | Checkpoints, preprocessing, class mapping, metric definitions, runtime settings |
| `artifact_hashes_before.json` | Pre-evaluation SHA-256 hashes |
| `artifact_hashes_after.json` | Post-evaluation SHA-256 hashes (all unchanged) |
| `baseline_test_metrics.json` | Newly reproduced baseline test metrics |
| `candidate_test_metrics.json` | Candidate test metrics from the actual run |
| `per_class_metrics.csv` | Class-level results for both models |
| `confusion_matrix_baseline.csv` | Baseline confusion matrix |
| `confusion_matrix_candidate.csv` | Candidate confusion matrix |
| `prediction_comparison.csv` | Per-sample predictions from both models |
| `evaluation_failures.csv` | No failures (empty, header only) |
| `evaluate_phase09.py` | Repeatable evaluation script |
| `evaluation_results.json` | Consolidated results and comparison summary |
| `phase_09_summary.md` | This document |

---

## 8. What the Results Support

1. **The aspect-preserving candidate outperforms the baseline on this test partition** across all aggregate metrics (accuracy +3.78 pp, macro-F1 +3.85 pp, balanced accuracy +3.81 pp).
2. **The reproduction of baseline metrics exactly matches the historical Phase 02 reference**, confirming methodological consistency.
3. **Three of four priority Rotten classes improved** (RottenBellpepper, RottenTomato, RottenPotato), but **RottenCarrot decreased slightly (−0.40 pp F1)**.
4. **No images failed**, and **artifact hashes remained unchanged**, confirming a clean, reproducible run.

---

## 9. What Remains Unverified

- **Independent acceptance:** This test partition was already used once. A fresh independent evaluation set is required before declaring production readiness.
- **Real-world generalization:** Labels are folder-derived; capture conditions and domain representativeness are unverified.
- **Application integration:** No model has been integrated into the application (`INTEGRATION_NOT_VERIFIED` from Phase 08).
- **Food-safety/freshness calibration:** Softmax scores are uncalibrated and do not represent food-safety or freshness probabilities.

---

## 10. Recommendation

**Proceed to independent evaluation.** The candidate shows a clear improvement over the baseline on this diagnostic test run (+3.85 pp macro-F1), but this partition is not independent. Before any acceptance or integration decision:

1. Obtain a fresh, independently collected or adjudicated evaluation set (not previously seen by either model).
2. Define pre-registered acceptance thresholds (accuracy, macro-F1, per-class minimums).
3. Run the candidate (and baseline) on that independent set under an approved protocol.
4. Only after independent acceptance should application integration be considered.

**Do not declare the candidate production-ready solely on this evaluation.**

---

## 11. Confirmation

- No models were trained, fine-tuned, or modified.
- No checkpoints, preprocessing configurations, class mappings, or labels were changed.
- No train/validation/test splits were generated or modified.
- No source images, labels, or split assignments were copied or altered.
- No previous phase reports, manifests, models, hashes, or inference scripts were modified.
- No datasets or external assets were downloaded.
- No dependencies were installed or upgraded.
- No application code was modified.
- No model integration was started.

Stop after Phase 09. Do not begin training or integration automatically.
