# Detection dataset validation

- Status: **BLOCKED** for complete training preparation.
- Configured class count: 63; contiguous IDs: True.
- Available decoded images: 180 (test: 180).
- Train/validation ZIP paths are Git LFS pointer text files, not archive payloads; expected sizes are captured in `exclusion_manifest.csv`.
- `data.yaml` points validation and test to the same `images/test` directory. Its comments state 7,221 validation and 180 test, but the available test directory contains 180 images.
- Annotation issues: 8 out-of-bounds box lines across 6 images (0 missing annotations; all referenced class IDs are in the 63-class mapping). Empty annotation files are retained as valid negative images.
- Exact duplicate groups: 0; see `duplicate_report.csv`.

No annotation was invented and no source files/config were changed. Restore the original LFS payloads and correct configuration only in a separately reviewed future phase before training.

