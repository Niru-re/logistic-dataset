# Phase 06 — Cold-chain, shelf-life and logistics data preparation

| Family | Actual size | Status | Key limitation |
|---|---:|---|---|
| Mango experiment | 563 source files; 47353 parsed time-series/quality rows | AUDIT_COMPLETE | Box/configuration association is plausible, but no complete validated sample/time crosswalk or shelf-life endpoint; no merged data/split. |
| Food Expiry | 200000 × 7 | BLOCKED | README and CSV schemas differ; target ground truth/provenance/IDs not established. |
| Dynamic logistics | 32065 × 26 | BLOCKED | Candidate targets and prediction-time semantics unknown; no shipment/trip IDs; leakage risk. |

Source integrity check: 568 files hashed before and after; unchanged = **True**. No model training or evaluation occurred. No source dataset files were edited.

## Next step

Obtain authoritative data dictionaries and collection/label-generation protocols for the two CSV datasets. For mango measurements, build and independently verify an experiment/box/fruit/date crosswalk and define a scientific quality or shelf-life endpoint before deciding on any prediction task. Then design group- and time-aware validation partitions before model work.
