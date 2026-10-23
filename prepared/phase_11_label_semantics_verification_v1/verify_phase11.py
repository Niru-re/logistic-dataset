"""
Phase 11 verification script (read-only).

Checks that all Phase 11 deliverable files exist, that referenced evidence
files exist, and that key counts are internally consistent.
Does NOT modify any source artifacts. Does NOT load models, run inference,
or calculate evaluation metrics. Does NOT touch the old test partition
beyond reading manifest hashes (already computed in prior phases).
"""

import csv
import json
import os
import sys
from pathlib import Path

PHASE11_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PHASE11_DIR.parent.parent.parent

DELIVERABLES = [
    "source_evidence_report.md",
    "label_semantics_decision.json",
    "test_overlap_report.json",
    "old_test_overlap_complete.json",
    "independent_eval_eligibility.csv",
    "excluded_candidates.csv",
    "unresolved_labels.csv",
    "evaluation_protocol_draft.md",
    "data_acquisition_requirements.md",
    "phase_11_summary.md",
    "README.md",
    "verify_phase11.py",
]

EVIDENCE_FILES = [
    PROJECT_ROOT / "datasets/prepared/phase_10_independent_eval_readiness_v1/independent_eval_manifest.csv",
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

    print("== Checking Phase 11 deliverable files ==")
    for name in DELIVERABLES:
        checks += 1
        check_file_exists(PHASE11_DIR / name, name, errors)

    print("== Checking referenced evidence files exist (read-only) ==")
    for path in EVIDENCE_FILES:
        checks += 1
        check_file_exists(path, str(path.relative_to(PROJECT_ROOT)), errors)

    # Check label_semantics_decision.json
    print("== Checking label_semantics_decision.json ==")
    lsd_path = PHASE11_DIR / "label_semantics_decision.json"
    if lsd_path.exists():
        data = json.loads(lsd_path.read_text(encoding="utf-8"))
        checks += 1
        print(f"  Evidence status: {data.get('label_semantics_evidence_status', 'N/A')}")
        print(f"  Classes eligible: {data.get('summary_counts', {}).get('classes_eligible_for_evaluation', 'N/A')}")
        checks += 1
        if data.get("label_semantics_evidence_status") != "UNVERIFIED":
            errors.append("label_semantics_decision.json: evidence status should be UNVERIFIED")
        checks += 1
        if data.get("summary_counts", {}).get("classes_eligible_for_evaluation") != 0:
            errors.append("label_semantics_decision.json: no classes should be eligible for evaluation")

    # Check independent_eval_eligibility.csv
    print("== Checking independent_eval_eligibility.csv ==")
    elig_path = PHASE11_DIR / "independent_eval_eligibility.csv"
    if elig_path.exists():
        rows = read_csv_rows(elig_path)
        checks += 1
        print(f"  Eligible records: {len(rows)}")
        # All should have overlap_old_test = "no"
        for r in rows:
            checks += 1
            if r.get("overlap_old_test") != "no":
                errors.append(f"independent_eval_eligibility.csv: record {r.get('sample_id')} has overlap_old_test != no")
            checks += 1
            if r.get("label_semantics_evidence_status") != "UNVERIFIED":
                errors.append(f"independent_eval_eligibility.csv: record {r.get('sample_id')} label semantics should be UNVERIFIED")
            checks += 1
            if r.get("final_eligibility_decision") != "NOT_ENDORSED_unverified_label_semantics":
                errors.append(f"independent_eval_eligibility.csv: record {r.get('sample_id')} should be NOT_ENDORSED")

    # Check excluded_candidates.csv
    print("== Checking excluded_candidates.csv ==")
    excl_path = PHASE11_DIR / "excluded_candidates.csv"
    if excl_path.exists():
        rows = read_csv_rows(excl_path)
        checks += 1
        print(f"  Excluded records: {len(rows)}")
        old_test_count = sum(1 for r in rows if "old_fr_test" in r.get("exclusion_reason", ""))
        print(f"  Excluded due to old-test overlap: {old_test_count}")
        checks += 1
        if old_test_count != 2200:
            errors.append(f"excluded_candidates.csv: expected 2200 old-test exclusions, found {old_test_count}")

    # Check test_overlap_report.json
    print("== Checking test_overlap_report.json ==")
    ovr_path = PHASE11_DIR / "test_overlap_report.json"
    if ovr_path.exists():
        data = json.loads(ovr_path.read_text(encoding="utf-8"))
        checks += 1
        counts = data.get("counts", {})
        print(f"  Overlap training: {counts.get('overlap_training', 'N/A')}")
        print(f"  Overlap validation: {counts.get('overlap_validation', 'N/A')}")
        print(f"  Overlap old test: {counts.get('overlap_old_test', 'N/A')}")
        checks += 1
        if counts.get("overlap_old_test") != 2200:
            errors.append(f"test_overlap_report.json: expected 2200 old-test overlaps, found {counts.get('overlap_old_test')}")

    # Check old_test_overlap_complete.json
    print("== Checking old_test_overlap_complete.json ==")
    otc_path = PHASE11_DIR / "old_test_overlap_complete.json"
    if otc_path.exists():
        data = json.loads(otc_path.read_text(encoding="utf-8"))
        checks += 1
        print(f"  Old-test overlap records: {data.get('old_test_overlap_count', 'N/A')}")
        checks += 1
        if data.get("old_test_overlap_count") != 2200:
            errors.append(f"old_test_overlap_complete.json: expected 2200 records, found {data.get('old_test_overlap_count')}")

    # Check unresolved_labels.csv
    print("== Checking unresolved_labels.csv ==")
    unr_path = PHASE11_DIR / "unresolved_labels.csv"
    if unr_path.exists():
        rows = read_csv_rows(unr_path)
        checks += 1
        print(f"  Unresolved records: {len(rows)}")

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
