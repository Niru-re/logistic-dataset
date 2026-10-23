# Phase 10 — Independent Fresh/Rotten Evaluation Dataset Readiness

**Project:** AgriChain AI  
**Phase:** 10 — Independent Fresh/Rotten Evaluation Dataset Readiness  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_10_independent_eval_readiness_v1`  
**Created:** 2026-10-17  
**Status:** Read-only audit and reporting.

---

## Purpose

Determine whether the project already contains a suitable, distinct source dataset for a future independent Fresh/Rotten evaluation of the frozen baseline and aspect-preserving candidate models. The Phase 09 diagnostic evaluation used the old 2,408-image test partition (previously used for baseline evaluation), so it is not an independent test set.

No model inference, training, or metric calculation was performed in this phase.

---

## Created Files

| File | Description |
|---|---|
| `source_candidate_registry.csv` | All source datasets considered and their suitability for Fresh/Rotten independent evaluation |
| `independent_eval_manifest.csv` | 17,309 eligible candidate samples from the Healthy & Rotten dataset. References original images only — no images copied. |
| `excluded_candidates.csv` | 10,204 excluded samples with reasons (8,604 overlap with FR train/val; 1,600 unmapped produce types) |
| `unresolved_labels.csv` | 5 conflicting Carrot__Healthy/Carrot__Rotten label records from the unresolved manifest |
| `overlap_report.json` | Exact-duplicate (sha256) overlap check between Healthy & Rotten and Fresh/Rotten train/validation data |
| `eligibility_analysis.json` | Detailed eligibility breakdown by class and split |
| `evaluation_protocol_draft.md` | Proposed future evaluation protocol (draft, not executed) |
| `data_acquisition_requirements.md` | Requirements if no adequate existing source is available |
| `phase_10_summary.md` | Consolidated findings, final readiness status, blockers, recommended next step |
| `README.md` | This file |
| `verify_phase10.py` | Reusable read-only verification script |

---

## Key Findings

- **Only one viable source:** Healthy & Rotten / Fruit And Vegetable Diseases Dataset (27,513 images)
- **Eligible for independent evaluation:** 17,309 images across all 20 Fresh/Rotten classes
- **Excluded — overlap with FR train/val:** 8,604 images (exact sha256 match)
- **Excluded — unmapped produce types:** 1,600 images (Grape, Guava, Jujube, Pomegranate)
- **Final readiness status:** `PREPARED_WITH_LIMITATIONS`

### Critical limitations

1. **Label semantics not verified:** Source is a "Diseases Dataset"; no documentation establishes Healthy=Fresh or Rotten=freshness ground truth.
2. **Independence not fully established:** Overlap with old 2,408-image test partition not checked (restricted in this phase).
3. **Class imbalance:** Priority Rotten classes have only 110-118 eligible samples each.

---

## Restrictions Honored

- No model inference, training, or metric calculation
- No model checkpoints loaded
- No old 2,408-image test partition opened, copied, hashed, or processed
- No source labels, mappings, or manifests changed
- No dependencies installed or upgraded
- No datasets downloaded
- No previous phase deliverables modified
- No application code modified

---

## How to Use

1. Review `phase_10_summary.md` for the consolidated findings and readiness status.
2. Review `evaluation_protocol_draft.md` for the proposed future evaluation protocol.
3. Review `independent_eval_manifest.csv` for the eligible sample references (original image paths only).
4. If pursuing label semantics verification, see `data_acquisition_requirements.md` for requirements.
5. Run `verify_phase10.py` to confirm all deliverables are present and internally consistent.

---

## Verification

Run `python verify_phase10.py` from this directory to confirm all files exist and key counts are consistent. The script is read-only and does not modify any source artifacts.
