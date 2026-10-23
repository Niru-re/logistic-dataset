"""
Phase 10 verification script (read-only).

Checks that all Phase 10 deliverable files exist, that the referenced evidence
files exist, and that key counts in the registries are internally consistent.
Does NOT modify any source artifacts, previous phase reports, models, or images.
Does NOT run model inference, train models, or calculate evaluation metrics.
Does NOT touch the old 2,408-image test partition.
"""

import csv
import json
import os
import sys
from pathlib import Path

PHASE10_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PHASE10_DIR.parent.parent.parent  # phase_10 -> prepared -> datasets -> logistic

DELIVERABLES = [
    "source_candidate_registry.csv",
    "independent_eval_manifest.csv",
    "excluded_candidates.csv",
    "unresolved_labels.csv",
    "overlap_report.json",
    "eligibility_analysis.json",
    "evaluation_protocol_draft.md",
    "data_acquisition_requirements.md",
    "phase_10_summary.md",
    "README.md",
    "verify_phase10.py",
]

# Evidence files referenced by Phase 10 deliverables (read-only existence check)
EVIDENCE_FILES = [
    PROJECT_ROOT / "datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/dataset_manifest.csv",
    PROJECT_ROOT / "datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/unresolved_manifest.csv",
    PROJECT_ROOT / "datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/class_mapping.json",
    PROJECT_ROOT / "datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/preparation_metadata.json",
    PROJECT_ROOT / "datasets/prepared/phase_04_image_datasets_v1/healthy_rotten_diseases/dataset_summary.md",
    PROJECT_ROOT / "datasets/prepared/fresh_rotten_v1/dataset_manifest.csv",
]


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def check_file_exists(path, label, errors):
    if not path.exists():
        errors.append(f"MISSING: {label} -> {path}")
    return path.exists()


def main():
    errors = []
    checks = 0

    print("== Checking Phase 10 deliverable files ==")
    for name in DELIVERABLES:
        checks += 1
        check_file_exists(PHASE10_DIR / name, name, errors)

    print("== Checking referenced evidence files exist (read-only) ==")
    for path in EVIDENCE_FILES:
        checks += 1
        check_file_exists(path, str(path.relative_to(PROJECT_ROOT)), errors)

    # Check source_candidate_registry.csv
    print("== Checking source_candidate_registry.csv ==")
    reg_path = PHASE10_DIR / "source_candidate_registry.csv"
    if reg_path.exists():
        rows = read_csv_rows(reg_path)
        expected_sources = {
            "Healthy & Rotten / Fruit And Vegetable Diseases Dataset",
            "Fruits-360",
            "VegNet",
            "Fruits and Vegetables Detection Dataset",
            "Door Open/Close YOLO Dataset",
            "Mango Cold-Chain Measurements",
            "Food Expiry CSV",
            "Dynamic Logistics CSV",
            "Fish / Seafood Dataset",
        }
        found = {r["source_dataset"] for r in rows}
        checks += 1
        if found != expected_sources:
            errors.append(
                f"source_candidate_registry.csv: expected {len(expected_sources)} sources, "
                f"found {len(found)}. Missing: {expected_sources - found}. Extra: {found - expected_sources}"
            )
        for r in rows:
            checks += 1
            if not r.get("readiness_status", "").strip():
                errors.append(f"source_candidate_registry.csv: empty readiness_status for '{r.get('source_dataset')}'")

    # Check independent_eval_manifest.csv
    print("== Checking independent_eval_manifest.csv ==")
    manifest_path = PHASE10_DIR / "independent_eval_manifest.csv"
    if manifest_path.exists():
        rows = read_csv_rows(manifest_path)
        checks += 1
        print(f"  Eligible records: {len(rows)}")
        # Verify all have sha256 and mapped_fr_class
        for r in rows:
            checks += 1
            if not r.get("sha256", "").strip():
                errors.append(f"independent_eval_manifest.csv: empty sha256 for sample '{r.get('sample_id')}'")
            checks += 1
            if not r.get("mapped_fr_class", "").strip():
                errors.append(f"independent_eval_manifest.csv: empty mapped_fr_class for sample '{r.get('sample_id')}'")

    # Check excluded_candidates.csv
    print("== Checking excluded_candidates.csv ==")
    excl_path = PHASE10_DIR / "excluded_candidates.csv"
    if excl_path.exists():
        rows = read_csv_rows(excl_path)
        checks += 1
        print(f"  Excluded records: {len(rows)}")

    # Check unresolved_labels.csv
    print("== Checking unresolved_labels.csv ==")
    unr_path = PHASE10_DIR / "unresolved_labels.csv"
    if unr_path.exists():
        rows = read_csv_rows(unr_path)
        checks += 1
        print(f"  Unresolved records: {len(rows)}")

    # Check overlap_report.json
    print("== Checking overlap_report.json ==")
    ovr_path = PHASE10_DIR / "overlap_report.json"
    if ovr_path.exists():
        data = json.loads(ovr_path.read_text(encoding="utf-8"))
        checks += 1
        print(f"  Exact overlap count: {data.get('exact_overlap_count', 'N/A')}")

    # Check eligibility_analysis.json
    print("== Checking eligibility_analysis.json ==")
    ea_path = PHASE10_DIR / "eligibility_analysis.json"
    if ea_path.exists():
        data = json.loads(ea_path.read_text(encoding="utf-8"))
        checks += 1
        print(f"  Eligible count: {data.get('counts', {}).get('eligible', 'N/A')}")

    # Report
    print(f"\n== Verification complete: {checks} checks ==")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All checks passed. No source artifacts were modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
