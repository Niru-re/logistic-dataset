# Phase 04 image dataset preparation

This directory contains manifests and quality reports for four existing datasets. CSV records point to original source files; images were not copied, transformed, renamed, relabeled, or deleted. No Fresh/Rotten model artifact or held-out image file was opened, hashed, decoded, or otherwise processed.

Each dataset folder contains `dataset_manifest.csv`, `exclusion_manifest.csv`, `unresolved_manifest.csv`, `class_mapping.json`, `preparation_metadata.json`, and `dataset_summary.md`. The detection folder also contains `annotation_validation.csv` and `duplicate_report.csv`. Exact same-label duplicate copies are excluded; conflicting-label duplicate groups and invalid detection samples are unresolved. Official partitions are preserved; where a classification dataset had no split, manifests use seed 2048 for deterministic 80/10/10 assignments after duplicate grouping.

To repeat safely, copy `prepare_phase04.py` to a fresh versioned output directory under `datasets/prepared` and run it there with `py -3 prepare_phase04.py`. It requires the already installed Python 3.13.7 and Pillow 12.1.1 and writes only derived manifests and reports. The script refuses to overwrite an existing dataset output unless explicitly passed `--replace-derived`. Image decoding does not establish label validity or model readiness.

The detection data is blocked for training: its train/validation image and label ZIPs are Git LFS pointer files, and `data.yaml` points both validation and test to `images/test`. See the dataset-specific summary before any further preparation.

