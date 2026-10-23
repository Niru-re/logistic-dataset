# Phase 08 Summary — Final Dataset Readiness Audit & ML Roadmap

**Project:** AgriChain AI
**Phase:** 08 — Final Dataset Readiness Audit & ML Roadmap (read-only)
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_08_dataset_readiness_v1`
**Created:** 2026-10-17

## Overview

This phase consolidated evidence from Phases 00–07 into one dataset readiness assessment. It is read-only: no models were trained, no datasets reprocessed, no files repaired, and nothing was integrated into the application. Every finding cites a supporting report or manifest.

## Dataset families — consolidation status

| # | Dataset family | Discovery | Audit | Preparation | Task suitability | Model status | Integration |
|---|---|---|---|---|---|---|---|
| A | Fresh/Rotten Produce (fresh_rotten_v1) | AUDIT_COMPLETE | AUDIT_COMPLETE | PREPARED | 20-class Fresh/Rotten produce image classification | Baseline: BASELINE_TEST_EVALUATED + INFERENCE_SMOKE_TESTED; Candidate: INFERENCE_SMOKE_TESTED only (validation-only metrics) | INTEGRATION_NOT_VERIFIED |
| B | Fruits-360 | AUDIT_COMPLETE | AUDIT_COMPLETE | PREPARED_WITH_LIMITATIONS | Produce variety recognition (268 classes); NOT freshness | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| C | Healthy & Rotten / Fruit And Vegetable Diseases | AUDIT_COMPLETE | AUDIT_COMPLETE | PREPARED_WITH_LIMITATIONS | Healthy/Rotten disease classification per produce type; freshness equivalence UNRESOLVED | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| D | VegNet | AUDIT_COMPLETE | AUDIT_COMPLETE | PREPARED_WITH_LIMITATIONS | Multi-state quality (Unripe/Ripe/Old/Dried/Damaged); NOT directly binary Fresh/Rotten | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| E | Fruits and Vegetables Detection Dataset | NOT_FOUND (payloads missing) | AUDIT_COMPLETE | BLOCKED | Fruits/vegetables object detection (63 classes) — BLOCKED | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| F | Door Open/Close YOLO | AUDIT_COMPLETE | AUDIT_COMPLETE | PREPARED_WITH_LIMITATIONS | Door Open/Close detection (2 classes); domain suitability UNRESOLVED | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| G | Mango Cold-Chain Measurements | AUDIT_COMPLETE | AUDIT_COMPLETE | AUDIT_COMPLETE | Temperature/humidity time-series; shelf-life contingent on validated endpoint | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| H | Food Expiry CSV | NOT_FOUND (for supervised use) | AUDIT_COMPLETE | BLOCKED | Shelf-life estimation only after target/provenance validation | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| I | Dynamic Logistics CSV | NOT_FOUND (for supervised use) | AUDIT_COMPLETE | BLOCKED | Shipment delay/risk prediction only after target/prediction-time definitions | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |
| J | Fish / Seafood | NOT_FOUND | NOT_FOUND | NOT_FOUND | None — no dataset located | NOT_TRAINED | INTEGRATION_NOT_VERIFIED |

### Summary of preparation statuses
- **PREPARED:** 1 (Fresh/Rotten)
- **PREPARED_WITH_LIMITATIONS:** 4 (Fruits-360, Healthy & Rotten, VegNet, Door Open/Close)
- **BLOCKED:** 3 (Fruits & Vegetables Detection, Food Expiry, Dynamic Logistics)
- **AUDIT_COMPLETE (no training manifest required):** 1 (Mango Cold-Chain)
- **NOT_FOUND:** 1 (Fish/Seafood)

## Models — what exists and what evidence supports it

### Baseline model (20-class Fresh/Rotten, SmallCNN)
- **Checkpoint:** `datasets\trained_models\fresh_rotten_v1\best_checkpoint.pt` (SHA-256: `82dd2d17...`)
- **Training evidence:** 12 epochs on CPU; train 7,497 / validation 1,876 samples.
- **Validation metrics (epoch 12):** macro-F1 0.8108; balanced accuracy 0.8108; loss 0.6273.
- **Held-out test metrics:** accuracy 0.7973; macro-F1 0.7981; balanced accuracy 0.7963; 488/2408 misclassified. Test used for inference/reporting only, not for model selection.
- **Inference package:** Phase 03 — 11/11 smoke tests PASS (authoritative rerun `smoke_test_report_run_2.json`); artifact hashes unchanged; synthetic images only.
- **Status:** TRAINED_VALIDATION_ONLY + BASELINE_TEST_EVALUATED + INFERENCE_SMOKE_TESTED + INDEPENDENT_EVALUATION_REQUIRED + INTEGRATION_NOT_VERIFIED.

### Aspect-preserving candidate model (20-class Fresh/Rotten, SmallCNN, aspect-preserving 96x96)
- **Checkpoint:** `datasets\trained_models\fresh_rotten_v1\aspect_preserving_96_experiment_v1\best_checkpoint.pt`
- **Training evidence:** 12 epochs on CPU; same train/validation split.
- **Validation metrics (epoch 12):** macro-F1 0.8404; balanced accuracy 0.8393; loss 0.5315. Pre-registered criteria met on validation.
- **Test metrics:** NOT evaluated on held-out test set.
- **Inference package:** Covered by same Phase 03 package (11/11 PASS).
- **Status:** TRAINED_VALIDATION_ONLY + INFERENCE_SMOKE_TESTED + INDEPENDENT_EVALUATION_REQUIRED + INTEGRATION_NOT_VERIFIED.

**Important:** The candidate's higher validation macro-F1 (84.04% vs baseline 81.08%) is validation-only evidence. It must NOT be interpreted as outperformance on test data. The candidate has not been evaluated on the existing test partition.

## Which capabilities have supporting data

| Capability | Supporting dataset | Status |
|---|---|---|
| Produce variety recognition | Fruits-360 | Data prepared; no model; evaluation protocol not valid (no validation split) |
| Fresh/Rotten visual classification | fresh_rotten_v1 | Prepared; baseline test-evaluated; candidate needs independent test eval |
| Multi-state produce quality | VegNet | Prepared with limitations; no model; quality criteria undocumented |
| Fruits/vegetables object detection | Fruits & Vegetables Detection | BLOCKED (missing LFS payloads, config conflict, out-of-bounds boxes) |
| Door Open/Close detection | Door Open-Close YOLO | Prepared with limitations; domain suitability unverified; leakage unresolved |
| Cold-storage visual monitoring / worker-activity | NO_VERIFIED_DATASET | No dataset identified — do not claim support |
| Temperature/humidity anomaly detection | Mango Cold-Chain | Audit complete; no crosswalk or endpoint defined |
| Temperature forecasting | Mango Cold-Chain | Audit complete; no target/horizon defined |
| Shelf-life estimation | Food Expiry (blocked) / Mango (contingent) | BLOCKED / contingent on endpoint definition |
| Shipment delay prediction | Dynamic Logistics | BLOCKED (no group IDs, leakage risk, target unresolved) |
| Shipment risk classification | Dynamic Logistics | BLOCKED (same as delay) |
| Fish/seafood recognition or quality | NO_VERIFIED_DATASET | NOT_FOUND |

## Tasks ready for a carefully scoped training experiment (after gates)

1. **Fresh/Rotten candidate independent test evaluation** — uses existing prepared test partition and Phase 03 inference package; no new source data needed. Highest-value next step.
2. **Label-provenance review and acceptance thresholds** for Fresh/Rotten — no new data needed.

Tasks blocked by missing files/broken annotations: Fruits & Vegetables Detection (B-07); Door Open/Close domain/leakage (B-08).
Tasks blocked by uncertain labels/targets: Healthy & Rotten freshness equivalence (B-05); VegNet quality-state mapping (B-06); Food Expiry ground truth (B-10); Dynamic Logistics target/prediction time (B-11); Mango shelf-life endpoint/crosswalk (B-09).
Tasks requiring a new independent evaluation dataset: Fresh/Rotten candidate acceptance (fresh independent set recommended after baseline test already used once).
Features not implemented/integrated: all models (INTEGRATION_NOT_VERIFIED); cold-storage visual monitoring and worker/activity analysis (no dataset); fish/seafood recognition (no dataset).

## Most important decisions

1. **Do not claim the aspect-preserving candidate outperforms the baseline.** The candidate's 84.04% validation macro-F1 is validation-only; it has never been evaluated on the held-out test set. Run an independent held-out test evaluation before any performance claim.
2. **Do not treat "Rotten" in Healthy & Rotten or VegNet quality states as verified Fresh/Rotten ground truth.** Label semantics are unresolved (5 Carrot conflicts; no documented visual criteria for VegNet's five states).
3. **Do not use Fruits-360 for freshness/shelf-life.** It is variety recognition on controlled studio imagery with no freshness encoding.
4. **Do not train shipment-risk or shelf-life models on the CSV datasets.** Targets, provenance, grouping, and prediction-time semantics are unverified; leakage risk is present.
5. **No model is integrated into the application.** All models are `INTEGRATION_NOT_VERIFIED`.

## Unresolved limitations (blocker register)

Fourteen blockers are recorded in `blocker_register.csv` (B-01 through B-14). Highest-priority unresolved items:
- **B-01:** Candidate model not test-evaluated (Fresh/Rotten).
- **B-02:** Fresh/Rotten label provenance/capture conditions unverified.
- **B-05:** Healthy & Rotten Carrot label conflicts + freshness equivalence undocumented.
- **B-07:** Detection dataset missing Git LFS payloads and `data.yaml` conflict.
- **B-08:** Door Open/Close domain suitability + source-group leakage unresolved.
- **B-09:** Mango no verified sample/time crosswalk or shelf-life endpoint.
- **B-10/B-11:** Food Expiry and Dynamic Logistics targets/provenance/group IDs unverified.
- **B-12:** Fish/seafood dataset not found.

## Recommended next phase

**Run an independent held-out test evaluation of the Fresh/Rotten aspect-preserving candidate model** using the existing prepared test partition (2,408 images) and the Phase 03 inference package, under a separately approved evaluation protocol. This is the highest-value, lowest-effort next step: it requires no new source data, uses already-prepared artifacts, and directly resolves the most important evidence gap (candidate test performance vs. baseline).

After that, complete the Fresh/Rotten label-provenance review and define acceptance thresholds (Phase A2/A3 in `phase_dependency_plan.md`). Only after those gates should any further training or application integration be scheduled.

## Exact output paths and created files

All files are under `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_08_dataset_readiness_v1\`:

- `dataset_registry.csv`
- `feature_readiness_matrix.csv`
- `model_registry.csv`
- `blocker_register.csv`
- `phase_dependency_plan.md`
- `README.md` (this file's companion)
- `phase_08_summary.md`

## Confirmation

No training, fine-tuning, or model evaluation occurred in this phase. No model metrics were recomputed from raw images. No Fresh/Rotten held-out test images were opened, copied, or re-evaluated. No source datasets or split assignments were modified. No previous phase reports, manifests, models, hashes, or inference scripts were modified. No annotations were repaired, no labels resolved, no new splits generated. No datasets or external assets were downloaded. No dependencies were installed or upgraded. No application code (React frontend, backend, database, API keys, environment variables) was modified. No new dataset-processing phase was started. No model or dataset was marked production-ready without evidence.

Stop after Phase 08. Do not begin training or integration automatically.
