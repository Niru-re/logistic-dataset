"""
Phase 09 — Fresh/Rotten Candidate Diagnostic Evaluation Script.

Read-only diagnostic evaluation. Compares the baseline and aspect-preserving
candidate checkpoints on the existing 2,408-image test partition. No training,
fine-tuning, or model modification.

Usage:
    python evaluate_phase09.py

All outputs are written to the phase_09_candidate_diagnostic_evaluation_v1
directory. Source images, labels, checkpoints, and manifests are never modified.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import torch
from PIL import Image, UnidentifiedImageError
from torch import nn

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(r"C:\Users\nirma\OneDrive\Desktop\logistic")
OUT = BASE / "datasets/trained_models/fresh_rotten_v1/phase_09_candidate_diagnostic_evaluation_v1"
MANIFEST = BASE / "datasets/prepared/fresh_rotten_v1/dataset_manifest.csv"
DATASET_ROOT = BASE / "datasets/Fruits-Vegetables-Dataset-main/Fruits-Vegetables-Dataset-main/split_dataset"

BASELINE_CKPT = BASE / "datasets/trained_models/fresh_rotten_v1/best_checkpoint.pt"
CANDIDATE_CKPT = BASE / "datasets/trained_models/fresh_rotten_v1/aspect_preserving_96_experiment_v1/best_checkpoint.pt"
BASELINE_MAPPING = BASE / "datasets/trained_models/fresh_rotten_v1/class_to_idx.json"
CANDIDATE_MAPPING = BASE / "datasets/trained_models/fresh_rotten_v1/aspect_preserving_96_experiment_v1/class_to_idx.json"
BASELINE_CONFIG = BASE / "datasets/trained_models/fresh_rotten_v1/training_config.json"
CANDIDATE_CONFIG = BASE / "datasets/trained_models/fresh_rotten_v1/aspect_preserving_96_experiment_v1/training_config.json"

IMAGE_SIZE = 96
BATCH_SIZE = 16
CPU_THREADS = 2
DEVICE = "cpu"

CLASS_ORDER = [
    "FreshApple", "FreshBanana", "FreshBellpepper", "FreshCarrot", "FreshCucumber",
    "FreshMango", "FreshOrange", "FreshPotato", "FreshStrawberry", "FreshTomato",
    "RottenApple", "RottenBanana", "RottenBellpepper", "RottenCarrot", "RottenCucumber",
    "RottenMango", "RottenOrange", "RottenPotato", "RottenStrawberry", "RottenTomato",
]
PRIORITY_CLASSES = ["RottenBellpepper", "RottenCarrot", "RottenTomato", "RottenPotato"]

torch.set_num_threads(CPU_THREADS)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class SmallCNN(nn.Module):
    def __init__(self, nclasses: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 24, 3, padding=1, bias=False),
            nn.BatchNorm2d(24),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(24, 48, 3, padding=1, bias=False),
            nn.BatchNorm2d(48),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(48, 96, 3, padding=1, bias=False),
            nn.BatchNorm2d(96),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(96, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.head = nn.Sequential(nn.Flatten(), nn.Dropout(0.25), nn.Linear(128, nclasses))

    def forward(self, x):  # noqa: D401
        return self.head(self.features(x))


# ---------------------------------------------------------------------------
# Preprocessing (identical to training scripts)
# ---------------------------------------------------------------------------
def preprocess_stretch(image: Image.Image) -> torch.Tensor:
    """Baseline: direct bilinear resize to 96x96."""
    image = image.convert("RGB")
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR)
    raw = bytearray(image.tobytes())
    x = torch.frombuffer(raw, dtype=torch.uint8).reshape(IMAGE_SIZE, IMAGE_SIZE, 3)
    x = x.permute(2, 0, 1).contiguous().to(dtype=torch.float32).div_(255.0)
    x.sub_(0.5).div_(0.5)
    if tuple(x.shape) != (3, IMAGE_SIZE, IMAGE_SIZE) or not bool(torch.isfinite(x).all()):
        raise ValueError("Invalid preprocessed tensor (stretch).")
    return x


def preprocess_aspect_preserving(image: Image.Image) -> torch.Tensor:
    """Candidate: aspect-preserving bilinear fit inside 96x96, center-pad RGB(127,127,127)."""
    image = image.convert("RGB")
    scale = min(IMAGE_SIZE / image.width, IMAGE_SIZE / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), (127, 127, 127))
    canvas.paste(image, ((IMAGE_SIZE - image.width) // 2, (IMAGE_SIZE - image.height) // 2))
    raw = bytearray(canvas.tobytes())
    x = torch.frombuffer(raw, dtype=torch.uint8).reshape(IMAGE_SIZE, IMAGE_SIZE, 3)
    x = x.permute(2, 0, 1).contiguous().to(dtype=torch.float32).div_(255.0)
    x.sub_(0.5).div_(0.5)
    if tuple(x.shape) != (3, IMAGE_SIZE, IMAGE_SIZE) or not bool(torch.isfinite(x).all()):
        raise ValueError("Invalid preprocessed tensor (aspect_preserving).")
    return x


# ---------------------------------------------------------------------------
# Checkpoint loading
# ---------------------------------------------------------------------------
def load_checkpoint_model(ckpt_path: Path, mapping: dict[str, int], label: str) -> SmallCNN:
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if not isinstance(ckpt, dict) or "model_state_dict" not in ckpt:
        raise ValueError(f"{label}: checkpoint lacks model_state_dict.")
    if ckpt.get("class_to_idx") != mapping:
        raise ValueError(f"{label}: checkpoint and sidecar class mappings differ.")
    model = SmallCNN(len(mapping))
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.to(DEVICE).eval()
    return model


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------
def load_test_rows() -> list[dict[str, str]]:
    rows = []
    with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("assigned_split") == "test":
                rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Metrics (identical definitions to training scripts)
# ---------------------------------------------------------------------------
def compute_metrics(confusion: list[list[int]], classes: list[str]) -> dict[str, Any]:
    n = len(classes)
    support = [sum(confusion[i]) for i in range(n)]
    total = sum(support)
    per_class = []
    recalls = []
    f1s = []
    for i in range(n):
        tp = confusion[i][i]
        fp = sum(confusion[j][i] for j in range(n)) - tp
        fn = support[i] - tp
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class.append({
            "class": classes[i],
            "support": support[i],
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })
        recalls.append(recall)
        f1s.append(f1)
    correct = sum(confusion[i][i] for i in range(n))
    accuracy = correct / total if total else 0.0
    macro_f1 = sum(f1s) / n if n else 0.0
    balanced_accuracy = sum(recalls) / n if n else 0.0
    misclassified = total - correct
    misclassification_rate = misclassified / total if total else 0.0
    return {
        "total_assigned": total,
        "evaluated": total,
        "failures": 0,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "balanced_accuracy": balanced_accuracy,
        "misclassified": misclassified,
        "misclassification_rate": misclassification_rate,
        "per_class": per_class,
        "confusion_matrix": confusion,
        "class_order": classes,
    }


def pp_diff(a: float, b: float) -> float:
    """Difference in percentage points (b - a)."""
    return (b - a) * 100.0


# ---------------------------------------------------------------------------
# Evaluation over a dataset
# ---------------------------------------------------------------------------
def evaluate_model(
    model: SmallCNN,
    test_rows: list[dict[str, str]],
    class_to_idx: dict[str, int],
    preprocess_fn,
    model_label: str,
) -> dict[str, Any]:
    n_classes = len(class_to_idx)
    confusion = [[0 for _ in range(n_classes)] for _ in range(n_classes)]
    failures: list[dict[str, str]] = []
    predictions: list[dict[str, Any]] = []
    processed = 0
    batch_inputs: list[torch.Tensor] = []
    batch_meta: list[dict[str, Any]] = []

    def flush_batch() -> None:
        nonlocal processed
        if not batch_inputs:
            return
        batch = torch.stack(batch_inputs)
        with torch.inference_mode():
            logits = model(batch.to(DEVICE))
            scores = torch.softmax(logits, dim=1)
        vals, inds = torch.topk(scores, k=min(5, n_classes), dim=1)
        for row_idx, meta in enumerate(batch_meta):
            true_class = meta["true_class"]
            pred_idx = int(inds[row_idx, 0].item())
            true_idx = class_to_idx[true_class]
            confusion[true_idx][pred_idx] += 1
            top_k = []
            for score, class_idx in zip(vals[row_idx].tolist(), inds[row_idx].tolist()):
                top_k.append({
                    "class_name": CLASS_ORDER[int(class_idx)],
                    "raw_softmax_score": float(score),
                })
            predictions.append({
                "input_identifier": meta["path"],
                "true_class": true_class,
                "predicted_class_name": CLASS_ORDER[pred_idx],
                "predicted_class_index": pred_idx,
                "true_class_index": true_idx,
                "correct": pred_idx == true_idx,
                "raw_predicted_class_softmax_score": float(scores[row_idx, pred_idx].item()),
                "top_k_predictions": top_k,
                "input_dimensions": meta["dims"],
                "inference_status": "success",
            })
        processed += len(batch_inputs)
        batch_inputs.clear()
        batch_meta.clear()

    start = time.perf_counter()
    for r in test_rows:
        rel = r["relative_path"]
        true_class = r["class"]
        img_path = DATASET_ROOT.joinpath(*rel.split("/"))
        try:
            with Image.open(img_path) as im:
                im.load()
                width, height = im.size
                if width < 1 or height < 1:
                    raise ValueError(f"Invalid image dimensions: {img_path}")
                tensor = preprocess_fn(im)
            batch_inputs.append(tensor)
            batch_meta.append({"path": str(img_path.resolve()), "true_class": true_class, "dims": {"width": width, "height": height}})
        except (UnidentifiedImageError, OSError, ValueError) as e:
            failures.append({
                "input_identifier": str(img_path),
                "relative_path": rel,
                "true_class": true_class,
                "reason": type(e).__name__ + ": " + str(e),
            })
        if len(batch_inputs) >= BATCH_SIZE:
            flush_batch()
    flush_batch()

    elapsed = time.perf_counter() - start
    evaluated = processed
    total_assigned = len(test_rows)

    # Rebuild confusion from predictions to keep it authoritative
    confusion2 = [[0 for _ in range(n_classes)] for _ in range(n_classes)]
    for p in predictions:
        confusion2[p["true_class_index"]][p["predicted_class_index"]] += 1

    metrics = compute_metrics(confusion2, CLASS_ORDER)
    metrics["evaluated"] = evaluated
    metrics["failures"] = len(failures)
    metrics["total_assigned"] = total_assigned
    metrics["elapsed_seconds"] = elapsed
    metrics["predictions"] = predictions
    metrics["failures_list"] = failures
    return metrics


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Load test rows
    test_rows = load_test_rows()
    print(f"Test rows from manifest: {len(test_rows)}")
    assert len(test_rows) == 2408, f"Expected 2408 test rows, got {len(test_rows)}"

    # Load mappings
    baseline_mapping = json.loads(BASELINE_MAPPING.read_text(encoding="utf-8"))
    candidate_mapping = json.loads(CANDIDATE_MAPPING.read_text(encoding="utf-8"))
    assert baseline_mapping == candidate_mapping, "Class mappings differ between models"
    assert baseline_mapping == {name: i for i, name in enumerate(CLASS_ORDER)}, "Class order mismatch"

    # Verify configs match preprocessing policies
    baseline_cfg = json.loads(BASELINE_CONFIG.read_text(encoding="utf-8"))
    candidate_cfg = json.loads(CANDIDATE_CONFIG.read_text(encoding="utf-8"))
    assert baseline_cfg["resize"] == "PIL bilinear RGB", f"Unexpected baseline resize: {baseline_cfg['resize']}"
    assert candidate_cfg["resize"] == "PIL bilinear RGB; aspect-preserving fit within 96x96, center-pad RGB(127,127,127)", \
        f"Unexpected candidate resize: {candidate_cfg['resize']}"

    # Load models
    print("Loading baseline model...")
    baseline_model = load_checkpoint_model(BASELINE_CKPT, baseline_mapping, "baseline")
    print("Loading candidate model...")
    candidate_model = load_checkpoint_model(CANDIDATE_CKPT, candidate_mapping, "candidate")

    # Evaluate
    print("Evaluating baseline on test partition...")
    baseline_results = evaluate_model(
        baseline_model, test_rows, baseline_mapping, preprocess_stretch, "baseline"
    )
    print(f"  Baseline: accuracy={baseline_results['accuracy']:.6f}, "
          f"macro_f1={baseline_results['macro_f1']:.6f}, "
          f"balanced_acc={baseline_results['balanced_accuracy']:.6f}, "
          f"evaluated={baseline_results['evaluated']}/{baseline_results['total_assigned']}, "
          f"failures={baseline_results['failures']}")

    print("Evaluating candidate on test partition...")
    candidate_results = evaluate_model(
        candidate_model, test_rows, candidate_mapping, preprocess_aspect_preserving, "candidate"
    )
    print(f"  Candidate: accuracy={candidate_results['accuracy']:.6f}, "
          f"macro_f1={candidate_results['macro_f1']:.6f}, "
          f"balanced_acc={candidate_results['balanced_accuracy']:.6f}, "
          f"evaluated={candidate_results['evaluated']}/{candidate_results['total_assigned']}, "
          f"failures={candidate_results['failures']}")

    # --- Save artifact hashes after ---
    hash_artifacts = {
        "baseline_checkpoint": BASELINE_CKPT,
        "candidate_checkpoint": CANDIDATE_CKPT,
        "baseline_class_mapping": BASELINE_MAPPING,
        "candidate_class_mapping": CANDIDATE_MAPPING,
        "baseline_training_config": BASELINE_CONFIG,
        "candidate_training_config": CANDIDATE_CONFIG,
        "baseline_training_script": BASE / "datasets/trained_models/fresh_rotten_v1/train_baseline.py",
        "candidate_training_script": BASE / "datasets/trained_models/fresh_rotten_v1/aspect_preserving_96_experiment_v1/train_aspect_preserving.py",
        "dataset_manifest": MANIFEST,
    }
    after_hashes = {k: sha256_file(v) for k, v in hash_artifacts.items()}

    before_path = OUT / "artifact_hashes_before.json"
    before_data = json.loads(before_path.read_text(encoding="utf-8"))
    before_hashes = {k: v["sha256"] for k, v in before_data["artifacts"].items()}

    hash_unchanged = all(
        before_hashes.get(k) == after_hashes.get(k) for k in before_hashes
    )
    print(f"\nArtifact hashes unchanged after evaluation: {hash_unchanged}")

    after_out = {
        "recorded_phase": "09_after",
        "hashes_unchanged": hash_unchanged,
        "artifacts": {k: {"path": str(v), "sha256": h} for k, v, h in zip(hash_artifacts.keys(), hash_artifacts.values(), after_hashes.values())},
    }
    (OUT / "artifact_hashes_after.json").write_text(
        json.dumps(after_out, indent=2), encoding="utf-8"
    )

    # --- Save baseline metrics ---
    baseline_report = {
        "model": "baseline",
        "model_name": "fresh_rotten_v1_baseline",
        "checkpoint": str(BASELINE_CKPT),
        "checkpoint_sha256": sha256_file(BASELINE_CKPT),
        "preprocessing_policy": "stretch",
        "preprocessing_description": "PIL RGB convert, direct bilinear resize to 96x96, tensor [0,1], normalize (x-0.5)/0.5",
        "total_assigned": baseline_results["total_assigned"],
        "evaluated": baseline_results["evaluated"],
        "failures": baseline_results["failures"],
        "accuracy": baseline_results["accuracy"],
        "macro_f1": baseline_results["macro_f1"],
        "balanced_accuracy": baseline_results["balanced_accuracy"],
        "misclassified": baseline_results["misclassified"],
        "misclassification_rate": baseline_results["misclassification_rate"],
        "elapsed_seconds": baseline_results["elapsed_seconds"],
        "device": DEVICE,
        "torch_threads": CPU_THREADS,
        "class_order": CLASS_ORDER,
        "per_class": baseline_results["per_class"],
        "confusion_matrix": baseline_results["confusion_matrix"],
    }
    (OUT / "baseline_test_metrics.json").write_text(
        json.dumps(baseline_report, indent=2), encoding="utf-8"
    )

    # --- Save candidate metrics ---
    candidate_report = {
        "model": "candidate",
        "model_name": "fresh_rotten_v1_aspect_preserving_96_experiment_v1",
        "checkpoint": str(CANDIDATE_CKPT),
        "checkpoint_sha256": sha256_file(CANDIDATE_CKPT),
        "preprocessing_policy": "aspect_preserving",
        "preprocessing_description": "PIL RGB convert, aspect-preserving bilinear fit inside 96x96, center-pad RGB(127,127,127), tensor [0,1], normalize (x-0.5)/0.5",
        "total_assigned": candidate_results["total_assigned"],
        "evaluated": candidate_results["evaluated"],
        "failures": candidate_results["failures"],
        "accuracy": candidate_results["accuracy"],
        "macro_f1": candidate_results["macro_f1"],
        "balanced_accuracy": candidate_results["balanced_accuracy"],
        "misclassified": candidate_results["misclassified"],
        "misclassification_rate": candidate_results["misclassification_rate"],
        "elapsed_seconds": candidate_results["elapsed_seconds"],
        "device": DEVICE,
        "torch_threads": CPU_THREADS,
        "class_order": CLASS_ORDER,
        "per_class": candidate_results["per_class"],
        "confusion_matrix": candidate_results["confusion_matrix"],
    }
    (OUT / "candidate_test_metrics.json").write_text(
        json.dumps(candidate_report, indent=2), encoding="utf-8"
    )

    # --- Per-class metrics CSV ---
    with (OUT / "per_class_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "class", "class_index", "support",
            "baseline_precision", "baseline_recall", "baseline_f1",
            "candidate_precision", "candidate_recall", "candidate_f1",
            "f1_diff_pp",
        ])
        baseline_pc = {p["class"]: p for p in baseline_results["per_class"]}
        candidate_pc = {p["class"]: p for p in candidate_results["per_class"]}
        for cls in CLASS_ORDER:
            bp = baseline_pc[cls]
            cp = candidate_pc[cls]
            w.writerow([
                cls, CLASS_ORDER.index(cls), bp["support"],
                f"{bp['precision']:.8f}", f"{bp['recall']:.8f}", f"{bp['f1']:.8f}",
                f"{cp['precision']:.8f}", f"{cp['recall']:.8f}", f"{cp['f1']:.8f}",
                f"{(cp['f1'] - bp['f1']) * 100:.4f}",
            ])

    # --- Confusion matrices ---
    with (OUT / "confusion_matrix_baseline.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["true_class\\predicted_class"] + CLASS_ORDER)
        for cls, row in zip(CLASS_ORDER, baseline_results["confusion_matrix"]):
            w.writerow([cls] + row)
    with (OUT / "confusion_matrix_candidate.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["true_class\\predicted_class"] + CLASS_ORDER)
        for cls, row in zip(CLASS_ORDER, candidate_results["confusion_matrix"]):
            w.writerow([cls] + row)

    # --- Prediction comparison ---
    baseline_preds = {p["input_identifier"]: p for p in baseline_results["predictions"]}
    candidate_preds = {p["input_identifier"]: p for p in candidate_results["predictions"]}
    with (OUT / "prediction_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "input_identifier", "relative_path", "true_class", "true_class_index",
            "baseline_predicted_class", "baseline_predicted_index", "baseline_correct",
            "candidate_predicted_class", "candidate_predicted_index", "candidate_correct",
            "baseline_score", "candidate_score",
            "baseline_correct_candidate_wrong", "candidate_correct_baseline_wrong",
            "both_correct", "both_wrong",
        ])
        for r in test_rows:
            pid = str(DATASET_ROOT.joinpath(*r["relative_path"].split("/")).resolve())
            bp = baseline_preds[pid]
            cp = candidate_preds[pid]
            b_correct = bp["correct"]
            c_correct = cp["correct"]
            w.writerow([
                pid, r["relative_path"], r["class"], baseline_mapping[r["class"]],
                bp["predicted_class_name"], bp["predicted_class_index"], b_correct,
                cp["predicted_class_name"], cp["predicted_class_index"], c_correct,
                f"{bp['raw_predicted_class_softmax_score']:.8f}",
                f"{cp['raw_predicted_class_softmax_score']:.8f}",
                b_correct and not c_correct,
                c_correct and not b_correct,
                b_correct and c_correct,
                (not b_correct) and (not c_correct),
            ])

    # --- Failures ---
    all_failures = baseline_results["failures_list"] + candidate_results["failures_list"]
    with (OUT / "evaluation_failures.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["input_identifier", "relative_path", "true_class", "reason", "model"])
        for fl in all_failures:
            w.writerow([
                fl["input_identifier"], fl.get("relative_path", ""), fl.get("true_class", ""),
                fl["reason"], "both",
            ])

    # --- Summary ---
    baseline_pc = {p["class"]: p for p in baseline_results["per_class"]}
    candidate_pc = {p["class"]: p for p in candidate_results["per_class"]}
    priority_summary = {}
    for cls in PRIORITY_CLASSES:
        bp = baseline_pc[cls]
        cp = candidate_pc[cls]
        priority_summary[cls] = {
            "baseline": {"precision": bp["precision"], "recall": bp["recall"], "f1": bp["f1"], "support": bp["support"]},
            "candidate": {"precision": cp["precision"], "recall": cp["recall"], "f1": cp["f1"], "support": cp["support"]},
            "f1_diff_pp": (cp["f1"] - bp["f1"]) * 100.0,
            "recall_diff_pp": (cp["recall"] - bp["recall"]) * 100.0,
            "precision_diff_pp": (cp["precision"] - bp["precision"]) * 100.0,
        }
    pri_mean_baseline = sum(baseline_pc[c]["f1"] for c in PRIORITY_CLASSES) / len(PRIORITY_CLASSES)
    pri_mean_candidate = sum(candidate_pc[c]["f1"] for c in PRIORITY_CLASSES) / len(PRIORITY_CLASSES)

    summary = {
        "phase": "09",
        "type": "diagnostic_comparison",
        "is_independent_acceptance": False,
        "test_partition_previously_used": True,
        "test_images_assigned": baseline_results["total_assigned"],
        "baseline_evaluated": baseline_results["evaluated"],
        "candidate_evaluated": candidate_results["evaluated"],
        "baseline_failures": baseline_results["failures"],
        "candidate_failures": candidate_results["failures"],
        "hashes_unchanged": hash_unchanged,
        "baseline": {
            "accuracy": baseline_results["accuracy"],
            "macro_f1": baseline_results["macro_f1"],
            "balanced_accuracy": baseline_results["balanced_accuracy"],
            "misclassified": baseline_results["misclassified"],
            "misclassification_rate": baseline_results["misclassification_rate"],
        },
        "candidate": {
            "accuracy": candidate_results["accuracy"],
            "macro_f1": candidate_results["macro_f1"],
            "balanced_accuracy": candidate_results["balanced_accuracy"],
            "misclassified": candidate_results["misclassified"],
            "misclassification_rate": candidate_results["misclassification_rate"],
        },
        "difference_percentage_points": {
            "accuracy": pp_diff(baseline_results["accuracy"], candidate_results["accuracy"]),
            "macro_f1": pp_diff(baseline_results["macro_f1"], candidate_results["macro_f1"]),
            "balanced_accuracy": pp_diff(baseline_results["balanced_accuracy"], candidate_results["balanced_accuracy"]),
        },
        "priority_classes": priority_summary,
        "priority_rotten_mean_f1": {
            "baseline": pri_mean_baseline,
            "candidate": pri_mean_candidate,
            "diff_pp": (pri_mean_candidate - pri_mean_baseline) * 100.0,
        },
        "historical_reference_baseline": {
            "accuracy": 0.7973421926910299,
            "macro_f1": 0.7980587319103833,
            "balanced_accuracy": 0.7962887522806291,
            "source": "test_evaluation_v1/test_metrics.json",
        },
        "candidate_validation_reference": {
            "macro_f1": 0.8404110567407027,
            "balanced_accuracy": 0.8392685863879142,
            "warning": "Validation metrics are not held-out test evidence",
        },
        "conclusion": (
            "Diagnostic comparison only; not independent acceptance. "
            "Test partition previously used for baseline evaluation."
        ),
    }
    (OUT / "evaluation_results.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("\n=== Phase 09 Evaluation Complete ===")
    print(f"Output directory: {OUT}")
    print(f"Baseline test accuracy: {baseline_results['accuracy']*100:.2f}%")
    print(f"Candidate test accuracy: {candidate_results['accuracy']*100:.2f}%")
    print(f"Accuracy diff: {pp_diff(baseline_results['accuracy'], candidate_results['accuracy']):+.2f} pp")
    print(f"Baseline test macro-F1: {baseline_results['macro_f1']*100:.2f}%")
    print(f"Candidate test macro-F1: {candidate_results['macro_f1']*100:.2f}%")
    print(f"Macro-F1 diff: {pp_diff(baseline_results['macro_f1'], candidate_results['macro_f1']):+.2f} pp")
    print(f"Hashes unchanged: {hash_unchanged}")


if __name__ == "__main__":
    main()
