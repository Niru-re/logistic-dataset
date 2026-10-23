# Phase 11 — Source Evidence Report

**Project:** AgriChain AI  
**Phase:** 11 — Label Semantics and Independent Evaluation Source Verification  
**Output directory:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_11_label_semantics_verification_v1`  
**Created:** 2026-10-17  
**Status:** Read-only evidence verification. No model loaded, trained, or evaluated.

---

## 1. Source Under Review

**Dataset:** Healthy & Rotten / Fruit And Vegetable Diseases Dataset  
**Local source path:** `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\healty_&_rotten\Fruit And Vegetable Diseases Dataset`  
**Public source identification:** `Fruit and Vegetable Disease (Healthy vs Rotten)`, associated with Muhammad Subhan on Kaggle (`https://www.kaggle.com/dsv/8463025`)

---

## 2. Local Documentation Evidence

### 2.1 Files present in source directory

A recursive inventory of the source directory found **only image files**:

| Extension | Count |
|---|---|
| .jpg | 17,384 |
| .png | 11,813 |
| .jpeg | 80 |
| .webp | 14 |
| **Total images** | **29,277** |

**No documentation files exist** in the source directory. Specifically absent:
- README.md, README.txt, or any readme variant
- LICENSE or license file
- data dictionary or label definitions
- CSV metadata describing label assignment
- JSON metadata describing provenance or collection conditions
- Notebook files documenting labeling methodology
- Any documentation of any kind

### 2.2 Phase 04 preparation reports

The Phase 04 preparation metadata (`datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/preparation_metadata.json`) states:

- "deterministic per-class 80/10/10 assignment after exact-duplicate grouping"
- Source is named "Fruit And Vegetable Diseases Dataset"
- 29,291 candidate images, 27,513 accepted
- 5 unresolved conflict records (Carrot__Healthy / Carrot__Rotten conflicting labels)
- No documentation of label semantics beyond folder names

The Phase 04 class mapping (`class_mapping.json`) explicitly states for every class:

> "Source root names this a Diseases Dataset. Not independently verified as food safety or shelf-life label."

And for the dataset as a whole:

> "Folder taxonomy pairs 14 produce types with Healthy/Rotten labels. Source root names this a Diseases Dataset; no documentation establishes that 'Rotten' is equivalent to Freshness ground truth."

The Phase 04 dataset summary (`dataset_summary.md`) confirms:

> "Source root names this a Diseases Dataset; no documentation establishes that 'Rotten' is equivalent to Freshness ground truth. No official split exists; deterministic grouped 80/10/10 splits use seed 2048 after conflicting duplicate groups are held unresolved."

---

## 3. Public Source Documentation Evidence

### 3.1 Kaggle source page

Attempted to access `https://www.kaggle.com/dsv/8463025` for original dataset documentation. No readable content was returned from this URL.

### 3.2 Assessment

A directory name or public data-card summary is **not** proof that labels are scientifically established freshness ground truth. The available public description discusses 28 folders representing healthy and rotten images across 14 produce types, while describing the dataset's purpose in terms of **disease detection** — not freshness classification.

---

## 4. Label-Semantics Evidence Questions

| Question | Answer | Evidence Source |
|---|---|---|
| What does `Healthy` mean operationally? | **Not documented** — no definition found in any local or accessible source | Zero documentation files in source directory; Phase 04 reports confirm no documentation |
| What does `Rotten` mean operationally? | **Not documented** — no definition found in any local or accessible source | Same as above |
| Label assignment method? | **Unknown** — no documentation of human inspection, measurement protocol, or automatic rules | Same as above |
| Distinguishes freshness/spoilage from disease/damage/ripeness? | **Not established** — source is named a "Diseases Dataset", suggesting disease detection rather than freshness | Source directory name; Phase 04 reports |
| Sample-level provenance documented? | **No** — no collection conditions, original source, or labeling history documented | Zero documentation files |
| Labels validly map to Fresh/Rotten classes? | **Not established** — no documentation supports the equivalence | Phase 04 class_mapping.json explicitly states "no documentation establishes that 'Rotten' is equivalent to Freshness ground truth" |

---

## 5. Label Methodology Assessment

The labels are **folder-derived** (image placed in `X__Healthy` or `X__Rotten` folder). No evidence was found explaining:

- How "Healthy" was determined (visual inspection? expert adjudication? absence of visible disease?)
- How "Rotten" was determined (visible spoilage? time-since-harvest? microbiological testing?)
- Whether "Rotten" includes disease-damaged produce that may still be fresh
- Whether "Healthy" includes underripe or overripe produce
- Whether labels distinguish freshness from food safety

**Conclusion:** The labeling protocol is **undocumented**. The directory names `Healthy` and `Rotten` are the only evidence for label meaning, which is insufficient to establish freshness ground truth.

---

## 6. Evidence Strength Summary

| Evidence Dimension | Status | Supporting Evidence |
|---|---|---|
| Source provenance documentation | NOT_FOUND | Zero documentation files in source directory |
| Label definition (Healthy) | UNVERIFIED | No operational definition found |
| Label definition (Rotten) | UNVERIFIED | No operational definition found |
| Label assignment method | UNVERIFIED | No documentation of how labels were assigned |
| Freshness vs. disease distinction | NOT_ESTABLISHED | Source named "Diseases Dataset"; purpose described as disease detection |
| Sample-level provenance | NOT_FOUND | No collection conditions or labeling history documented |
| Valid mapping to Fresh/Rotten classes | UNVERIFIED | Phase 04 reports explicitly state no documentation establishes equivalence |

---

## 7. Conclusion

**No authoritative label documentation was found.** The source directory contains only images — no README, no data dictionary, no label definitions, no provenance records. Phase 04 preparation reports explicitly state that no documentation establishes the equivalence of "Rotten" to freshness ground truth. The public source page could not be accessed for additional documentation.

**Label semantics decision: UNVERIFIED for all classes.** The directory names `Healthy` and `Rotten` alone do not constitute credible documentation of freshness ground truth.
