# Phase 05 status

**PREPARED_WITH_LIMITATIONS**

- Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\Door Open-Close.v1i.yolov8`
- Images inventoried: 706
- Declared classes: 0 Door-Close; 1 Door-Open
- Source splits preserved: train / valid / test.
- Image decoding uses Pillow full decode; no images copied.
- Annotations checked for format, class IDs, normalized coordinates, positive box sizes, and image bounds.

## Split counts
- train: 559 images, 559 labels; instances {'Door-Close': 458, 'Door-Open': 91}; labeled images {'Door-Close': 457, 'Door-Open': 91}; empty labels 11; missing 0; orphan 0.
- valid: 75 images, 75 labels; instances {'Door-Close': 65, 'Door-Open': 8}; labeled images {'Door-Close': 65, 'Door-Open': 8}; empty labels 2; missing 0; orphan 0.
- test: 72 images, 72 labels; instances {'Door-Close': 58, 'Door-Open': 12}; labeled images {'Door-Close': 58, 'Door-Open': 12}; empty labels 2; missing 0; orphan 0.

- Exact duplicate groups/files: 0 / 0.
- Near duplicate candidates (aHash distance <=4): 228579; cross-split candidates: 80640.
- Filename-derived source groups spanning splits: 3 (candidate leakage; verify video/session provenance).
- Image decode errors: 0; invalid annotations: 0; unresolved records: 4.

## Configuration finding
The source `data.yaml` paths resolve relative to the YAML directory to a sibling `train/valid/test` tree, while this export actually stores split directories under the dataset root. `proposed_data.yaml` supplies a separate corrected relative configuration for this prepared output directory. Original configuration remains unchanged.

## Limitations
Near-duplicate screening is a lightweight aHash candidate search and does not establish visual identity. Filename-derived source groups are heuristic indicators of correlated frames and do not establish capture provenance. No annotations were semantically adjudicated. See CSV/JSON reports for per-file records.

No model training, inference, external API calls, or source edits were performed. A human review of class semantics and capture-level split leakage is still required before training.
