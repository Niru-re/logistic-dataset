# Phase 10 — Data Acquisition Requirements (Fresh/Rotten Independent Evaluation)

**Project:** AgriChain AI  
**Phase:** 10 — Independent Fresh/Rotten Evaluation Dataset Readiness  
**Status:** Requirements specification (no download or acquisition performed in this phase)

---

## 1. Current Situation

The Healthy & Rotten / Fruit And Vegetable Diseases Dataset is the only existing source with produce freshness/rotten labels that could support an independent Fresh/Rotten evaluation. However, it cannot yet serve as a fully independent evaluation source because:

1. **Label semantics unverified:** The source is a "Diseases Dataset." No documentation establishes that "Healthy" = "Fresh" or "Rotten" = freshness ground truth.
2. **Independence not fully established:** 8,604 images overlap with Fresh/Rotten training/validation data (excluded from eligible manifest). Overlap with the old 2,408-image test partition could not be checked (restricted in this phase).
3. **Class imbalance:** Eligible samples range from 110 to 2,624 per class, with priority classes (RottenBellpepper, RottenCarrot, RottenTomato, RottenPotato) having only 110-118 eligible samples each.

Because of these limitations, an independent evaluation set meeting all requirements does **not yet exist** in the project.

---

## 2. Required Data Characteristics

A suitable independent Fresh/Rotten evaluation dataset should meet the following requirements:

### 2.1 Label semantics

- **Freshness labels:** Each image must have a verified label indicating fresh vs. rotten/spoiled condition.
- **Produce type:** Each image must have a verified produce type (apple, banana, bell pepper, carrot, cucumber, mango, orange, potato, strawberry, tomato).
- **Mapping to model classes:** Each image's (produce type, freshness) combination must map unambiguously to one of the 20 Fresh/Rotten model classes:
  - FreshApple, FreshBanana, FreshBellpepper, FreshCarrot, FreshCucumber, FreshMango, FreshOrange, FreshPotato, FreshStrawberry, FreshTomato
  - RottenApple, RottenBanana, RottenBellpepper, RottenCarrot, RottenCucumber, RottenMango, RottenOrange, RottenPotato, RottenStrawberry, RottenTomato
- **Documentation:** A data dictionary or label-generation protocol must establish that the freshness labels are equivalent to the model's Fresh/Rotten target.

### 2.2 Independence

- **No overlap with model-development data:** No image may be an exact duplicate (sha256) of any image in the Fresh/Rotten training (7,497 images) or validation (1,876 images) partitions.
- **No overlap with prior test data:** No image may overlap with the old 2,408-image test partition used in Phase 02/Phase 09.
- **Documented collection origin:** The dataset should have a separate, documented collection or capture process distinct from the model-development data.

### 2.3 Sample size

- **Minimum per class:** At least 100 images per class (20 classes × 100 = 2,000 minimum total).
- **Recommended:** At least 500 images per class for robust per-class metric estimation, especially for priority classes.
- **Class balance:** Reasonably balanced across classes, or at minimum sufficient samples in each class for meaningful per-class F1 estimation.

### 2.4 Image characteristics

- **Format:** Decodable image files (JPEG, PNG, or similar) that can be loaded with Pillow.
- **Resolution:** Any resolution acceptable (models resize to 96x96 during preprocessing).
- **Content:** Single produce item per image, representative of real-world deployment conditions (not exclusively controlled studio backgrounds, unless deployment context matches).

---

## 3. Acquisition Options

### Option A: Verify and use existing Healthy & Rotten dataset

If authoritative documentation becomes available verifying that:
- "Healthy" labels correspond to "Fresh" ground truth
- "Rotten" labels correspond to freshness/rotten ground truth

and if overlap with the old test partition is verified as absent, then the 17,309 eligible Healthy & Rotten images could be used as an independent evaluation set.

**Required actions:**
1. Obtain data dictionary or label-generation protocol from the dataset source.
2. Verify label semantics (Healthy → Fresh, Rotten → Rotten).
3. Check overlap with old 2,408-image test partition (sha256 comparison).
4. Address class imbalance (consider stratified sampling or class-aware metrics).

### Option B: Collect a new independent evaluation dataset

If Option A is not feasible, collect a new dataset specifically for independent Fresh/Rotten evaluation:

**Required actions:**
1. Define collection protocol (produce types, freshness definitions, capture conditions).
2. Collect images for all 20 model classes with sufficient per-class samples.
3. Obtain verified ground truth labels (e.g., expert adjudication, controlled spoilage experiments).
4. Document collection origin, capture conditions, and label-generation method.
5. Compute sha256 hashes and verify no overlap with any existing project data.
6. Create evaluation manifest referencing original images without copying.

### Option C: Obtain an external freshness dataset

Identify and acquire an external dataset with verified freshness/rotten labels for the 10 produce types in the Fresh/Rotten model:

**Required actions:**
1. Identify candidate external datasets.
2. Verify label semantics and mapping to the 20 model classes.
3. Verify independence from project model-development data (sha256 overlap check).
4. Obtain distribution rights and documentation.
5. Create evaluation manifest referencing original images without copying.

---

## 4. Constraints for This Phase

- **Do not download datasets or external assets.** (Restriction)
- **Do not install or upgrade dependencies.** (Restriction)
- Acquisition must occur in a future phase, not this phase.
- This document specifies requirements only; no acquisition is performed here.

---

## 5. Recommended Next Step

1. Pursue Option A first: request label semantics documentation for the Healthy & Rotten dataset.
2. If Option A fails, proceed to Option B or C with a defined collection/acquisition protocol.
3. Only after an independent evaluation set is verified, execute the evaluation protocol draft (`evaluation_protocol_draft.md`).
