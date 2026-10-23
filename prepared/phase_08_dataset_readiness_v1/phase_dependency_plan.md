# Phase 08 — Dependency-Ordered Next-Step Plan

This plan orders the next project phases by dependency, evidence, risk, and usefulness to the AgriChain AI product. It distinguishes **data preparation**, **model training**, **independent evaluation**, and **application integration**. No training, reprocessing, or integration is performed in this phase.

## Guiding rules (from Phase 08 mandate)

- Do not train merely to demonstrate activity when data semantics or evaluation protocol are unreliable.
- Do not automatically choose the highest image-count dataset as the next training target.
- Do not download datasets or external assets in this phase.
- Do not modify source datasets, previous phase reports, manifests, models, hashes, or inference scripts.
- Keep dataset preparation status separate from training readiness and model readiness.

---

## Phase A — Unblocked, evidence-ready work (no new source data required)

These steps can proceed immediately using existing prepared artifacts.

### A1. Independent held-out test evaluation of the Fresh/Rotten candidate model
- **Type:** Independent evaluation
- **Depends on:** Existing prepared fresh_rotten_v1 test partition (2,408 images) and the candidate checkpoint (`aspect_preserving_96_experiment_v1\best_checkpoint.pt`) plus the Phase 03 inference package.
- **Action:** Run the candidate checkpoint on the existing held-out test set using a separately approved evaluation protocol. Compare against baseline test metrics (accuracy 79.73%, macro-F1 79.81%) only as a reference; do not infer superiority until test evidence exists.
- **Blockers resolved:** B-01.
- **Owner:** ML evaluation lead.

### A2. Fresh/Rotten label-provenance review
- **Type:** Data preparation / audit
- **Depends on:** Existing fresh_rotten_v1 preparation metadata and exclusion manifest.
- **Action:** Document label provenance, capture conditions, and domain representativeness for the 20 folder-derived classes. Do not modify labels; record findings.
- **Blockers resolved:** B-02 (partially).
- **Owner:** Data-quality auditor.

### A3. Document acceptance thresholds for Fresh/Rotten models
- **Type:** Evaluation governance
- **Depends on:** Baseline test metrics (test_evaluation_v1).
- **Action:** Define pre-registered acceptance thresholds (accuracy, macro-F1, per-class minimums) before any future model is compared against the baseline.
- **Blockers resolved:** B-14 (partially).
- **Owner:** ML lead + product.

---

## Phase B — Blocked by missing files or broken annotations (requires external resolution, no download in this phase)

### B1. Fruits and Vegetables Detection Dataset — restore LFS payloads and correct configuration
- **Type:** Data preparation
- **Depends on:** Git LFS access to the original train/validation archive payloads (external to this project tree).
- **Action:** Restore missing Git LFS payloads; correct `data.yaml` so validation and test point to distinct directories; re-run annotation audit (8 out-of-bounds box lines across 6 images); verify the 63-class mapping against `data.yaml`.
- **Blockers resolved:** B-07.
- **Prerequisite:** Access to Git LFS storage / original archive payloads (must not be downloaded as part of this phase; schedule for a later phase with authorized access).
- **Owner:** Data engineer.

### B2. Door Open/Close — verify domain provenance and resolve source-group leakage
- **Type:** Data preparation
- **Depends on:** Source video/session provenance documentation (external).
- **Action:** Verify whether the dataset captures refrigerated vehicles or cold-storage doors (domain suitability); resolve the 3 filename-derived source groups that may span splits; define a leakage-resistant group-aware evaluation; semantically annotate the 15 empty-annotation images and 4 unresolved records.
- **Blockers resolved:** B-08.
- **Prerequisite:** Capture-domain documentation; annotator review.
- **Owner:** Data-quality auditor + domain expert.

---

## Phase C — Blocked by uncertain labels or target definitions (requires authoritative documentation)

### C1. Healthy & Rotten — adjudicate label conflicts and establish freshness semantics
- **Type:** Data preparation
- **Depends on:** Authoritative label documentation / human adjudication.
- **Action:** Resolve the 5 conflicting Carrot__Healthy/Carrot__Rotten duplicate-byte records; document whether "Rotten" maps to freshness ground truth or to a disease state.
- **Blockers resolved:** B-05.
- **Prerequisite:** Human label adjudication; source documentation.
- **Owner:** Data-quality auditor + domain expert.

### C2. VegNet — document quality-state criteria and map to operational target
- **Type:** Data preparation
- **Depends on:** Source documentation / domain expert definitions.
- **Action:** Obtain documented visual criteria for the 5 quality states (Unripe, Ripe, Old, Dried, Damaged); address the empty Tomato/Dried class and class imbalance (27–1,234); decide whether a multi-state quality target or a derived binary freshness target is defensible.
- **Blockers resolved:** B-06.
- **Prerequisite:** Domain expert review.
- **Owner:** Data-quality auditor + domain expert.

### C3. Food Expiry CSV — obtain data dictionary and establish ground truth
- **Type:** Data preparation
- **Depends on:** Authoritative data dictionary and label-generation protocol (external).
- **Action:** Resolve README/CSV schema mismatch; establish `Expiry_days` provenance and ground truth; handle 9 missing category values; investigate temperature/category inconsistencies.
- **Blockers resolved:** B-10.
- **Prerequisite:** Authoritative data documentation (not to be downloaded in this phase).
- **Owner:** Data engineer.

### C4. Dynamic Logistics CSV — define prediction time, target, and group IDs
- **Type:** Data preparation
- **Depends on:** Authoritative data dictionary and collection/label-generation protocol (external).
- **Action:** Define prediction time and target semantics; establish shipment/trip/vehicle identifiers for group-based validation; exclude post-event/leakage fields (e.g., `delivery_time_deviation`).
- **Blockers resolved:** B-11.
- **Prerequisite:** Authoritative data documentation (not to be downloaded in this phase).
- **Owner:** Data engineer.

### C5. Mango Cold-Chain — build verified sample crosswalk and define shelf-life endpoint
- **Type:** Data preparation
- **Depends on:** Source documentation and scientific domain input.
- **Action:** Build and independently verify an experiment/box/fruit/date/time crosswalk; define a scientifically supported shelf-life or quality endpoint; handle 774 blank/NA cells and the questionable L_D12 measurement; resolve README/disk count discrepancies.
- **Blockers resolved:** B-09.
- **Prerequisite:** Source documentation; scientific review.
- **Owner:** Data-quality auditor + domain expert.

---

## Phase D — Requires an external dataset or authoritative documentation (must not be downloaded in this phase)

### D1. Fish/seafood recognition or quality assessment
- **Type:** External dataset acquisition + discovery
- **Depends on:** A fish/seafood dataset made available under the project dataset tree or the designated raw-data path (`C:\Users\nirma\OneDrive\Desktop\AgriChain_AI\data\raw`, which does not currently exist), with documentation and labels.
- **Action:** Repeat Phase 07 discovery and validation once the dataset is available.
- **Blockers resolved:** B-12.
- **Prerequisite:** External dataset delivery (out of scope for this phase).
- **Owner:** Data engineer.

### D2. Cold-storage visual monitoring and worker/activity analysis
- **Type:** External dataset identification
- **Depends on:** Identification and verification of an appropriate source dataset (none currently exists in the project).
- **Action:** No supported dataset exists today (`NO_VERIFIED_DATASET`). Identify a candidate source before claiming capability support.
- **Blockers resolved:** None yet (no dataset identified).
- **Prerequisite:** Candidate source identification.
- **Owner:** Product + data engineer.

---

## Phase E — Model training (only after Phases A–C prerequisites are met)

Training should not be scheduled until the corresponding evaluation protocol and label/target semantics are resolved.

| Training target | Required prerequisite phases | Readiness gate |
|---|---|---|
| Fresh/Rotten candidate (test evaluation) | Phase A1, A2 | Independent test evaluation complete; acceptance thresholds defined (A3) |
| Fruits-360 variety recognition | Phase B-equivalent (validation split + label adjudication) | Validation split created; labels adjudicated; domain shift assessed |
| Healthy & Rotten freshness/disease | Phase C1 | Label conflicts resolved; freshness semantics documented |
| VegNet multi-state quality | Phase C2 | Quality criteria documented; target mapping decided; imbalance addressed |
| Detection (Fruits/Veg) | Phase B1 | LFS payloads restored; data.yaml corrected; annotation audit re-run |
| Door Open/Close | Phase B2 | Domain verified; leakage resolved; group-aware evaluation defined |
| Shelf-life / temperature forecasting | Phase C3, C4, C5 | Ground truth/provenance established; endpoints defined; group/time-aware splits designed |
| Shipment delay/risk | Phase C4 | Prediction time/target defined; group IDs established; leakage excluded |

---

## Phase F — Application integration

- **Depends on:** Independent evaluation passed and acceptance thresholds met for a chosen model.
- **Action:** Integrate the verified model into the React frontend/backend/API; verify end-to-end inference; document integration status. Currently `INTEGRATION_NOT_VERIFIED` for all models (B-13).
- **Prerequisite:** A model with independent evaluation evidence and accepted metrics.

---

## Sequence summary (dependency order)

1. Phase A1 — Candidate independent test evaluation (highest value, no new data)
2. Phase A2 — Label-provenance review
3. Phase A3 — Acceptance thresholds
4. Phase B1 — Detection LFS restore + config fix (external access)
5. Phase B2 — Door Open/Close domain + leakage review
6. Phase C1–C5 — Label/target remediation (authoritative documentation required)
7. Phase D1/D2 — External dataset identification/acquisition (not downloaded this phase)
8. Phase E — Scoped model training only after gates are met
9. Phase F — Application integration only after evaluation gates are met
