# Phase 04 image dataset preparation summary

No model training or inference was run. The source files are unchanged; the outputs are path-referencing manifests and reports.

| Dataset | Status | Accepted images | Classes | Exclusions / findings |
|---|---|---:|---:|---|
| Fruits-360 | PREPARED_WITH_LIMITATIONS | 190873 | 268 | duplicates removed: 3; decode/other exclusions: 0 |
| Healthy & Rotten / Fruit And Vegetable Diseases Dataset | PREPARED_WITH_LIMITATIONS | 27513 | 28 | same-label duplicates removed: 1773; unresolved label-conflict records: 5 |
| VegNet | PREPARED_WITH_LIMITATIONS | 6150 | 20 | duplicates removed: 0; decode/other exclusions: 0 |
| Fruits and Vegetables Detection Dataset | BLOCKED | 180 | 63 | 180 test images available; 8 invalid box lines across 6 images; 0 missing labels; 4 train/val image/label LFS pointers; blocked |

## Recommended next phase

Restore the missing detection dataset LFS objects, reconcile its `data.yaml` split paths and class documentation, then re-run only its annotation audit. For classification, conduct label-semantics review before treating Healthy/Rotten or VegNet quality labels as operational cold-chain outcomes. Model training should be separately authorized after those reviews.


