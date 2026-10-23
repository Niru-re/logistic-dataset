# Phase 11 — Data Acquisition Requirements

**Project:** AgriChain AI  
**Phase:** 11 — Label Semantics and Independent Evaluation Source Verification  
**Status:** Requirements specification (no download or acquisition performed in this phase)

---

## 1. Current Conclusion

The Healthy & Rotten / Fruit And Vegetable Diseases Dataset **cannot** currently serve as an independent Fresh/Rotten evaluation source because:

1. **Label semantics are UNVERIFIED:** No documentation establishes that Healthy/Rotten labels map to Fresh/Rotten ground truth. The source is a "Diseases Dataset" with purpose described as disease detection.
2. **2,200 images overlap with the old test partition:** These were excluded from the eligible set in this phase.
3. **No class mapping is endorsed:** All 28 class mappings are UNVERIFIED or CONFLICTED; 0 classes are eligible for evaluation.

**Final readiness status: BLOCKED** — the available source evidence does not support defensible independent evaluation.

---

## 2. Requirement A: Verify Label Semantics (Primary Blocker)

### Required evidence

Obtain authoritative documentation from the dataset publisher (Kaggle dsv/8463025, Muhammad Subhan) establishing:

1. **Operational definition of "Healthy":** What criteria determine that a produce item is "Healthy"? (Visual inspection? Absence of visible disease? Expert adjudication? Time-since-harvest?)
2. **Operational definition of "Rotten":** What criteria determine that a produce item is "Rotten"? (Visible spoilage? Microbiological testing? Time-since-harvest thresholds?)
3. **Label assignment method:** Were labels assigned by documented human inspection, a measurement protocol, another dataset's labels, automatic rules, or an unknown method?
4. **Freshness vs. disease distinction:** Do the labels distinguish freshness/spoilage from disease, damage, ripeness, or appearance?
5. **Mapping validity:** Can "Healthy" be validly mapped to "Fresh" and "Rotten" to "Rotten" without changing the meaning of either label?

### Acceptable evidence types

- Dataset publisher's data dictionary or label definitions
- Original collection protocol or methodology documentation
- Peer-reviewed publication describing the dataset creation
- Official dataset documentation from the original publisher

### Unacceptable evidence

- Directory names alone (`Healthy`, `Rotten`)
- Third-party notebooks or repositories that merely repeat folder names
- Derivative models or reports that assume label equivalence without documentation
- Visual inspection of images to infer label meaning

---

## 3. Requirement B: Independent Evaluation Data

If label semantics cannot be verified for the existing source, a new independent evaluation dataset is required:

### Required data characteristics

- **Freshness labels:** Each image must have a verified label indicating fresh vs. rotten/spoiled condition
- **Produce type:** Each image must have a verified produce type (apple, banana, bell pepper, carrot, cucumber, mango, orange, potato, strawberry, tomato)
- **Mapping to model classes:** Each (produce type, freshness) combination must map unambiguously to one of the 20 Fresh/Rotten model classes
- **Documentation:** A data dictionary or label-generation protocol establishing label equivalence
- **Independence:** No image may be an exact duplicate of any image in Fresh/Rotten training (7,497), validation (1,876), or old test (2,408) partitions
- **Sample size:** Minimum 100 images per class (2,000 total); recommended 500+ per class for robust per-class metrics
- **Class balance:** Reasonably balanced across classes, especially priority classes (RottenBellpepper, RottenCarrot, RottenTomato, RottenPotato)

### Acquisition options

**Option A:** Obtain label documentation for Healthy & Rotten dataset, then use the 15,109 hash-independent candidates (if semantics verified)

**Option B:** Collect a new independent evaluation dataset with verified freshness labels for all 20 model classes

**Option C:** Acquire an external freshness dataset with verified labels and documented provenance

---

## 4. Constraints for This Phase

- **Do not download datasets or external assets.**
- **Do not install or upgrade dependencies.**
- Acquisition must occur in a future phase, not this phase.
- This document specifies requirements only; no acquisition is performed here.

---

## 5. Recommended Next Step

1. Pursue Requirement A: request label semantics documentation from the dataset publisher.
2. If Requirement A cannot be satisfied, proceed to Requirement B with a defined collection protocol.
3. Only after label semantics are verified AND an independent evaluation set is confirmed, execute the evaluation protocol draft.
4. Stop after Phase 11. Do not begin model evaluation or integration automatically.
