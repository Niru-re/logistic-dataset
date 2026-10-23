# Phase 11 — Label Semantics and Independent Evaluation Source Verification

**Project:** AgriChain AI  
**Phase:** 11 — Label Semantics and Independent Evaluation Source Verification  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_11_label_semantics_verification_v1`  
**Created:** 2026-10-17  
**Status:** Read-only audit and reporting.

---

## Purpose

Determine whether the existing Healthy & Rotten / Fruit And Vegetable Diseases dataset can legitimately support an independent Fresh/Rotten evaluation of the frozen baseline and aspect-preserving candidate models. Two questions:

1. Is there credible documentation explaining what `Healthy` and `Rotten` labels mean?
2. Do eligible candidate images overlap with previously used Fresh/Rotten training, validation, or test data?

No model inference, training, or metric calculation was performed.

---

## Created Files

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
| `data_acquisition_requirements.md` | Requirements if no adequate existing source |
| `phase_11_summary.md` | Consolidated findings, final readiness status, recommended next step |
| `README.md` | This file |
| `verify_phase11.py` | Reusable read-only verification script |

---

## Key Findings

- **Label documentation:** NOT FOUND — zero documentation files in source directory; only images exist
- **Label semantics:** UNVERIFIED for all 28 classes — no documentation establishes Healthy/Rotten → Fresh/Rotten
- **Old test partition overlap:** 2,200 images (excluded from eligible set)
- **Training/validation overlap:** 0 images
- **Candidates passing overlap checks:** 15,109 (but NOT endorsed due to unverified label semantics)
- **Final endorsed evaluation samples:** 0
- **Final readiness status:** BLOCKED

---

## Restrictions Honored

- No model inference, training, or metric calculation
- No model checkpoints loaded
- No old 2,408-image test partition visually inspected or used for inference
- Image bytes read solely for SHA-256 hash overlap verification (permitted in Phase 11)
- No source labels, mappings, or manifests changed
- No dependencies installed or upgraded
- No datasets downloaded
- No previous phase deliverables modified
- No application code modified

---

## Verification

Run `python verify_phase11.py` from this directory to confirm all deliverables exist and key counts are consistent. Read-only; does not modify any source artifacts.
