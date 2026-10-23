# Phase 06 data-preparation audit

Read `phase_06_summary.md`, then each family `dataset_summary.md`. Manifests preserve raw values and source row numbers; no rows were silently cleaned or dropped. Empty exclusion manifests mean no cleaned dataset was produced and therefore no records were excluded. No split manifest was generated where grouping or target semantics are insufficient. `phase_06_prepare.py` reruns the read-only inventory and report generation using Python standard library. Source hashes are checked before and after each run.
