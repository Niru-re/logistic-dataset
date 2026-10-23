# Fresh/Rotten blinded label review pack

## Contents
- contact_sheet_*.jpg: randomized visual sheets showing neutral review IDs only.
- human_review.csv: enter a decision, brief observation, and rationale for each ID. It omits folder labels and paths.
- reference_mapping.csv: separate source mapping. Keep it closed until the image-level review is recorded.

## Review procedure
1. Review each image using only its appearance. Record a brief observable description and rationale.
2. Choose exactly one decision: Consistent with label, Ambiguous, Potentially inconsistent, or Insufficient visual evidence.
3. Keep ambiguous cases unresolved; do not force a binary result. Potentially inconsistent requests deliberate human adjudication; it is not an automatic relabel.
4. After blinded decisions are recorded, use the separate mapping to compare against the folder-derived label. Preserve the original decision record and document any later adjudication separately.
5. Do not infer internal food quality, food safety, or remaining shelf life from visible appearance alone.

## Sampling and scope
- Random seed: 2048.
- Classes: RottenBellpepper, FreshBellpepper, RottenCarrot, FreshCarrot, RottenTomato, FreshTomato, RottenPotato, FreshPotato.
- Target: 20 images per class where eligible. Selected records are assigned to train or validation by the existing manifest only.
- Selection includes eligible Phase 02D candidates, then reproducible samples. Exact SHA-256 duplicates are avoided within the pack. IDs and gallery order are shuffled across classes and splits.
- No test-assigned images, test predictions, inference, training, or label edits were used.

Total images: 160. Contact sheets contain 20 images per page except the final page.
