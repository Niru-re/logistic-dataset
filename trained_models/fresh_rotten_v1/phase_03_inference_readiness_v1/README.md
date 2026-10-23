# Phase 03 — Fresh/Rotten inference readiness

This package is standalone. It does not connect to or modify the React application, backend, database, or external APIs.

## Verified models
- Candidate (default): fresh_rotten_v1_aspect_preserving_96_experiment_v1. Uses its matching checkpoint and aspect-preserving resize pipeline.
- Baseline (explicit): fresh_rotten_v1_baseline. Uses the original square-stretch pipeline and remains the reference model.

Both checkpoints use the verified 20-class SmallCNN (Conv-BatchNorm-ReLU channels 24/48/96/128, adaptive average pooling, dropout 0.25, linear 20-class head), RGB input at 96x96, Pillow bilinear interpolation, and float32 normalization approximately to [-1,1]. Candidate images preserve aspect ratio, fit within 96x96, then center-pad with RGB(127,127,127). Baseline images stretch directly to 96x96.

## Use
Add this directory to the Python import path:

    from inference_module import load_predictor
    predictor = load_predictor("candidate")  # or explicitly "baseline"
    one = predictor.predict_one(r"C:\path\to\image.jpg", top_k=5)
    many = predictor.predict_batch([r"C:\a.jpg", r"C:\b.png"], top_k=5)

Batch input must be a sequence of image paths. top_k is positive and clamped to the class count. Missing files raise FileNotFoundError, invalid or unsupported images raise ValueError, and unsupported input types raise TypeError. Checkpoint, mapping, preprocessing, and architecture incompatibilities raise clear load errors.

Successful results include input path, model/version/checkpoint, predicted class, parsed produce type and Fresh/Rotten label, raw predicted-class softmax score, top-k classes and scores, original dimensions, preprocessing configuration, and success status. Raw softmax scores are uncalibrated model scores. They are not calibrated freshness probabilities, food-safety assessments, or estimates of remaining shelf life or shipment survival.

## Smoke tests
Run:

    python smoke_test.py

The script creates temporary synthetic images inside this directory and removes only that temporary folder at exit. Tests exercise model loading, single and batch predictions, mapping, output shape and score validity, missing/invalid files, single/batch consistency, CPU inference, repeatability, and before/after model artifact hashes. Synthetic predictions are pipeline checks only, not accuracy evidence.

## Runtime and limitations
Verified environment: Python 3.10.0, PyTorch 2.2.1+cpu, Pillow 10.4.0, NumPy 2.2.6; CUDA unavailable. PyTorch emits a NumPy ABI warning. The implementation uses Pillow bytes and torch.frombuffer, avoiding the NumPy bridge. Palette images with transparency may emit a Pillow warning during conversion, as with the existing training path. Candidate validation metrics are not test-set or real-world performance evidence.