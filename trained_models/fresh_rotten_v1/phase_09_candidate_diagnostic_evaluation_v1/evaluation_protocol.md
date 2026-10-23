# Phase 09 — Fresh/Rotten Candidate Diagnostic Evaluation Protocol

**Project:** AgriChain AI  
**Phase:** 09 — Fresh/Rotten Candidate Diagnostic Evaluation  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\trained_models\fresh_rotten_v1\phase_09_candidate_diagnostic_evaluation_v1`  
**Created:** 2026-10-17  
**Status:** Read-only diagnostic evaluation. No training, fine-tuning, or model modification.

---

## 1. Purpose

This is a **comparative diagnostic evaluation**, not an independent final acceptance test. It evaluates the existing aspect-preserving Fresh/Rotten candidate model against the original baseline using the existing 2,408-image test partition. The goal is to assess comparative evidence, not to declare production readiness.

---

## 2. Test Partition Status (Diagnostic, Not Independent)

- The existing test partition contains **2,408 images** across 20 classes.
- The **original baseline was previously evaluated** on these same 2,408 images (Phase 02 held-out test evaluation, `test_evaluation_v1`).
- The **candidate has not previously been evaluated** on this partition, according to available reports (`test_split_loaded_or_evaluated: false` in candidate run_metadata).
- Because the baseline has already seen this partition during evaluation, this test set is **diagnostic, not independent or untouched**.
- No new test split is created. The established test assignments in the existing prepared dataset manifest (`datasets/prepared/fresh_rotten_v1/dataset_manifest.csv`, `assigned_split == "test"`) are used verbatim.
- Train and validation images are **never** used in test metrics.

---

## 3. Frozen Model Artifacts

- **Baseline checkpoint:** `datasets/trained_models/fresh_rotten_v1/best_checkpoint.pt` (SmallCNN, stretch-to-square 96x96 preprocessing).
- **Candidate checkpoint:** `datasets/trained_models/fresh_rotten_v1/aspect_preserving_96_experiment_v1/best_checkpoint.pt` (SmallCNN, aspect-preserving fit within 96x96 + center-pad RGB(127,127,127) preprocessing).
- Both checkpoints and preprocessing configurations are **frozen**. No weights, class mappings, labels, image assignments, or preprocessing are changed.
- The same 20-class mapping is used for both models (verified against `class_to_idx.json` sidecars and checkpoint metadata).
- If a checkpoint or preprocessing cannot be verified, that model's evaluation stops and the blocker is reported rather than guessed.

---

## 4. Execution Constraints

- No training, fine-tuning, or model selection occurs in this phase.
- Test results are **not** used for further training, tuning, or model selection.
- No new numeric acceptance threshold is established by previous project phases.
- Both models are evaluated in **one controlled run** using the same evaluation script and identical metric definitions, so metric calculations are consistent.
- CPU execution only (compatible with the existing environment; CUDA unavailable).
- `model.eval()` and `torch.inference_mode()` are used.
- Softmax scores are uncalibrated and are **not** described as calibrated freshness, food-safety probability, or shipment-survival estimates.
- Test images are **not** copied into the output directory. Prediction records store source references only.

---

## 5. Metrics

For each model, the following are calculated and reported:

- Total assigned test images (from manifest: 2,408).
- Successfully processed images and any failures.
- Accuracy.
- Macro-F1 (mean of per-class F1 scores).
- Balanced accuracy (mean of per-class recall).
- Per-class precision, recall, F1-score, and support.
- Confusion matrix (rows = true class, columns = predicted class).
- Number and percentage of misclassifications.

**Priority classes** (reported individually and as an aggregate):
- `RottenBellpepper`
- `RottenCarrot`
- `RottenTomato`
- `RottenPotato`

Metric differences between candidate and baseline are reported in **percentage points** for percentage-based metrics. Percentage-point differences are not confused with relative percentage improvements.

If any images fail to load or process, their paths and reasons are documented in `evaluation_failures.csv`. Failures are never silently removed from the denominator; both the full assigned count and the evaluated count are reported.

---

## 6. Class Order and Label Mapping

The verified 20-class order (alphabetical, casefold sort) is:

1. FreshApple (0)
2. FreshBanana (1)
3. FreshBellpepper (2)
4. FreshCarrot (3)
5. FreshCucumber (4)
6. FreshMango (5)
7. FreshOrange (6)
8. FreshPotato (7)
9. FreshStrawberry (8)
10. FreshTomato (9)
11. RottenApple (10)
12. RottenBanana (11)
13. RottenBellpepper (12)
14. RottenCarrot (13)
15. RottenCucumber (14)
16. RottenMango (15)
17. RottenOrange (16)
18. RottenPotato (17)
19. RottenStrawberry (18)
20. RottenTomato (19)

The same label order and metric definitions are used for both models.

---

## 7. Historical Reference (Not New Results)

Previously reported baseline test metrics (Phase 02, `test_evaluation_v1/test_metrics.json`):
- Accuracy: 79.73% (0.7973421926910299)
- Macro-F1: 79.81% (0.7980587319103833)
- Balanced accuracy: 79.63% (0.7962887522806291)
- Test images: 2,408
- Misclassified: 488/2,408

These are **historical reference figures**, not new results from this phase. A newly reproduced baseline run will be compared against them; any discrepancy will be investigated and documented, not silently replaced.

Earlier candidate validation results (Phase 02, `final_validation_metrics.json`):
- Accuracy: 84.28%
- Macro-F1: 84.04%
- Balanced accuracy: 83.93%

These validation metrics remain **clearly separated** from all test metrics. No candidate test result is presented until actually measured.

---

## 8. Artifact Protection

SHA-256 hashes of the baseline checkpoint, candidate checkpoint, class mappings, and relevant configuration files are recorded **before** evaluation (`artifact_hashes_before.json`) and verified **after** evaluation (`artifact_hashes_after.json`).

The following are **not** modified or overwritten:
- Original baseline artifacts
- Candidate training artifacts
- Phase 03 inference package
- Phase 04 dataset manifests
- Phase 08 reports or registries
- Original images, labels, and split assignments

Only new evaluation artifacts are saved in the Phase 09 output directory.

---

## 9. Limitations

- This evaluation uses a test partition already used once for baseline evaluation; results are diagnostic, not independent acceptance evidence.
- Labels are folder-derived; dataset provenance and capture conditions are not independently established.
- PyTorch 2.2.1+cpu with NumPy 2.2.6 emits an ABI warning; inference avoids the NumPy bridge (Pillow bytes + `torch.frombuffer`), consistent with prior phases.
- No GPU/CUDA is available; CPU execution with 2 Torch threads.
- Better image classification does **not** prove food safety, calibrated freshness probability, or shipment survival.

---

## 10. Output Files

- `evaluation_protocol.md` — this document
- `evaluation_config.json` — checkpoints, preprocessing, class mapping, metric definitions, runtime settings
- `artifact_hashes_before.json` — pre-evaluation SHA-256 hashes
- `artifact_hashes_after.json` — post-evaluation SHA-256 hashes
- `baseline_test_metrics.json` — newly reproduced baseline metrics
- `candidate_test_metrics.json` — candidate test metrics from the actual run
- `per_class_metrics.csv` — class-level results for both models
- `confusion_matrix_baseline.csv` — baseline confusion matrix
- `confusion_matrix_candidate.csv` — candidate confusion matrix
- `prediction_comparison.csv` — per-sample predictions from both models
- `evaluation_failures.csv` — failed records and reasons (if any)
- `evaluate_phase09.py` — repeatable evaluation script
- `phase_09_summary.md` — results, comparison, limitations, recommended next step
