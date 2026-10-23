"""
Phase 08 verification script (read-only).

Checks that all Phase 08 deliverable files exist, that the referenced evidence
files exist, and that key counts/statuses in the registries are internally
consistent. Does NOT modify any source artifacts, previous phase reports, models,
hashes, or inference scripts. Does NOT train or evaluate any model.

Usage:
    python verify_phase08.py
"""

import csv
import os
import sys

# Resolve paths relative to this script's location (Phase 08 output directory).
PHASE08_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE08_DIR, os.pardir, os.pardir, os.pardir))

DELIVERABLES = [
    "dataset_registry.csv",
    "feature_readiness_matrix.csv",
    "model_registry.csv",
    "blocker_register.csv",
    "phase_dependency_plan.md",
    "README.md",
    "phase_08_summary.md",
]

# Evidence files that the registries reference. These are checked for existence
# only (read-only); no content is modified.
EVIDENCE_FILES = [
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "fresh_rotten_v1", "preparation_metadata.json"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "fresh_rotten_v1", "dataset_manifest.csv"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "fresh_rotten_v1", "exclusion_manifest.csv"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "best_checkpoint.pt"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "run_metadata.json"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "final_validation_metrics.json"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "test_evaluation_v1", "evaluation_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "test_evaluation_v1", "test_metrics.json"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "phase_03_inference_readiness_v1", "phase_03_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "phase_03_inference_readiness_v1", "smoke_test_report_run_2.json"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "aspect_preserving_96_experiment_v1", "run_metadata.json"),
    os.path.join(PROJECT_ROOT, "datasets", "trained_models", "fresh_rotten_v1", "aspect_preserving_96_experiment_v1", "final_validation_metrics.json"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "phase_04_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "dataset_registry.csv"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "fruits_360", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "healthy_rotten_diseases", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "vegnet", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_04_image_datasets_v1", "fruits_vegetables_detection", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_05_door_open_close_v1", "phase_05_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_05_door_open_close_v1", "dataset_metadata.json"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_05_door_open_close_v1", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_06_cold_chain_shelf_life_v1", "phase_06_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_06_cold_chain_shelf_life_v1", "dataset_registry.csv"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_06_cold_chain_shelf_life_v1", "mango_cold_chain", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_06_cold_chain_shelf_life_v1", "food_expiry", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_06_cold_chain_shelf_life_v1", "dynamic_logistics", "dataset_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_07_fish_dataset_v1", "discovery_report.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_07_fish_dataset_v1", "phase_07_summary.md"),
    os.path.join(PROJECT_ROOT, "datasets", "prepared", "phase_07_fish_dataset_v1", "dataset_registry.csv"),
]


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_file_exists(path, label, errors):
    if not os.path.exists(path):
        errors.append(f"MISSING: {label} -> {path}")
    return os.path.exists(path)


def main():
    errors = []
    checks = 0

    # 1. All deliverable files exist.
    print("== Checking Phase 08 deliverable files ==")
    for name in DELIVERABLES:
        checks += 1
        check_file_exists(os.path.join(PHASE08_DIR, name), name, errors)

    print("== Checking referenced evidence files exist (read-only) ==")
    for path in EVIDENCE_FILES:
        checks += 1
        check_file_exists(path, os.path.relpath(path, PROJECT_ROOT), errors)

    # 2. Internal consistency of dataset_registry.csv.
    print("== Checking dataset_registry.csv ==")
    reg_path = os.path.join(PHASE08_DIR, "dataset_registry.csv")
    if os.path.exists(reg_path):
        rows = read_csv_rows(reg_path)
        expected_datasets = {
            "Fresh/Rotten Produce (fresh_rotten_v1)",
            "Fruits-360",
            "Healthy & Rotten / Fruit And Vegetable Diseases",
            "VegNet",
            "Fruits and Vegetables Detection Dataset",
            "Door Open/Close YOLO",
            "Mango Cold-Chain Measurements",
            "Food Expiry CSV",
            "Dynamic Logistics CSV",
            "Fish / Seafood Dataset",
        }
        found = {r["Dataset name"] for r in rows}
        checks += 1
        if found != expected_datasets:
            errors.append(
                f"dataset_registry.csv: expected {len(expected_datasets)} dataset rows, "
                f"found {len(found)}. Missing: {expected_datasets - found}. Extra: {found - expected_datasets}"
            )
        # Each row must have a non-empty source path and evidence reference.
        for r in rows:
            checks += 1
            if not r.get("Source path", "").strip():
                errors.append(f"dataset_registry.csv: empty Source path for '{r.get('Dataset name')}'")
            checks += 1
            if not r.get("Evidence report reference", "").strip():
                errors.append(f"dataset_registry.csv: empty Evidence report reference for '{r.get('Dataset name')}'")

    # 3. Internal consistency of feature_readiness_matrix.csv.
    print("== Checking feature_readiness_matrix.csv ==")
    mat_path = os.path.join(PHASE08_DIR, "feature_readiness_matrix.csv")
    expected_capabilities = {
        "Produce variety recognition",
        "Fresh/Rotten visual classification",
        "Multi-state produce quality classification",
        "Fruits/vegetables object detection",
        "Door Open/Close detection",
        "Cold-storage visual monitoring and worker/activity analysis",
        "Temperature/humidity anomaly detection",
        "Temperature forecasting",
        "Shelf-life estimation",
        "Shipment delay prediction",
        "Shipment risk classification",
        "Fish/seafood recognition or quality assessment",
    }
    if os.path.exists(mat_path):
        rows = read_csv_rows(mat_path)
        found = {r["AgriChain AI capability"] for r in rows}
        checks += 1
        if found != expected_capabilities:
            errors.append(
                f"feature_readiness_matrix.csv: expected {len(expected_capabilities)} capability rows, "
                f"found {len(found)}. Missing: {expected_capabilities - found}. Extra: {found - expected_capabilities}"
            )

    # 4. Internal consistency of model_registry.csv.
    print("== Checking model_registry.csv ==")
    model_path = os.path.join(PHASE08_DIR, "model_registry.csv")
    if os.path.exists(model_path):
        rows = read_csv_rows(model_path)
        checks += 1
        if len(rows) < 2:
            errors.append(f"model_registry.csv: expected baseline and candidate rows, found {len(rows)}")
        for r in rows:
            checks += 1
            if not r.get("Checkpoint location", "").strip():
                errors.append(f"model_registry.csv: empty Checkpoint location for '{r.get('Model variant')}'")

    # 5. Internal consistency of blocker_register.csv (unique IDs).
    print("== Checking blocker_register.csv ==")
    blocker_path = os.path.join(PHASE08_DIR, "blocker_register.csv")
    if os.path.exists(blocker_path):
        rows = read_csv_rows(blocker_path)
        ids = [r["Blocker ID"] for r in rows]
        checks += 1
        if len(ids) != len(set(ids)):
            errors.append(f"blocker_register.csv: duplicate Blocker ID values found: {ids}")
        checks += 1
        if len(rows) != 14:
            errors.append(f"blocker_register.csv: expected 14 blockers, found {len(rows)}")

    # 6. Verify model metrics are not duplicated across splits (validation vs test kept separate).
    print("== Checking model metric separation ==")
    if os.path.exists(model_path):
        rows = read_csv_rows(model_path)
        for r in rows:
            val_metrics = r.get("Reported metrics (validation)", "")
            test_metrics = r.get("Reported metrics (split)", "")
            checks += 1
            if "validation" in test_metrics.lower() and "test" in val_metrics.lower():
                errors.append(f"model_registry.csv: validation/test metrics may be conflated for '{r.get('Model variant')}'")

    # Report.
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
