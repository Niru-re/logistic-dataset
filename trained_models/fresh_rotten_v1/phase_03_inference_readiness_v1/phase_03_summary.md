# Phase 03 — Inference readiness summary

## Verified
- Both the original baseline and aspect-preserving candidate checkpoint were found and loaded successfully on CPU.
- The baseline and candidate use the same 166,252-parameter SmallCNN architecture and the same 20-class mapping, verified against each training config, sidecar mapping, and checkpoint payload.
- Both inputs are RGB 96x96 with the same bilinear interpolation and normalization to approximately [-1,1].
- Baseline preprocessing stretches directly to 96x96. Candidate preprocessing preserves aspect ratio, fits inside 96x96, and center-pads with RGB(127,127,127). The inference interface verifies these settings against each model's own training script/config and uses the matching policy.
- Candidate validation metrics (accuracy 84.28%, macro-F1 84.04%, balanced accuracy 83.93%) are recorded as validation-only results. They are not test or real-world performance evidence.

## Functional verification
The corrected smoke report records 11 passed and 0 failed checks: candidate and baseline loading/inference, candidate single and batch calls, output fields/count, mapping, finite score bounds, missing/invalid inputs, single/batch equivalence, CPU execution, and repeatability. All inference tests used temporary synthetic images only. No held-out test image or label was accessed.

The first smoke report was retained without overwrite. Its checks passed, but a timer-order bug made its per-test elapsed values invalid. The authoritative rerun is smoke_test_report_run_2.json, which records measured durations.

SHA-256 hashes for all 9 baseline-root files and 10 candidate-root files were recorded before testing and matched afterward. The prior test_evaluation_v1 directory was excluded from this hashing scope and was not accessed.

## Limitations
- PyTorch 2.2.1+cpu emits its existing ABI warning with NumPy 2.2.6. The inference module avoids the NumPy bridge with Pillow byte buffers and torch.frombuffer; smoke tests passed without environment changes.
- Pillow emits a palette-transparency warning in the environment. RGB conversion follows the verified training path.
- Synthetic smoke tests verify the interface and runtime path only. They do not establish model accuracy, calibration, robustness, or production readiness.
- No real image inference, test-set evaluation, application integration, backend/database work, or external API call was performed.
- Raw softmax scores are uncalibrated scores. They are not food-safety, shelf-life, or shipment-survival predictions.

## Recommended next step
Review the standalone package. Before application integration or acceptance claims, define a new independently collected or adjudicated evaluation set and a separately approved evaluation protocol.