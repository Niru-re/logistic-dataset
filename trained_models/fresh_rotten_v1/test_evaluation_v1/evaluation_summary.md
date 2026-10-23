# Fresh/Rotten baseline - held-out test evaluation

- Frozen checkpoint epoch 12; SHA-256: 82dd2d1784b794187665aaeb2ac340deee8b1b530c8cb5981d7ec22214960049.
- Test set: 2408 images across 20 classes; all test images loaded successfully.
- Top-1 accuracy: 0.7973.
- Macro-F1: 0.7981 (validation 0.8108; delta -0.0127).
- Balanced accuracy: 0.7963 (validation 0.8108; delta -0.0145).
- Misclassified 488/2408; inference time 12.9 seconds.
- Manifest SHA-256: 4a5c1fc7628335b15ffc37b31327934121142701cfe78c4817b3f69293eefbfc; cross-split hash-overlap counts: {'train_validation': 0, 'train_test': 0, 'validation_test': 0}.
- Test data was used for inference/reporting only, not training, checkpoint selection, or hyperparameter selection.
- No pre-existing acceptance thresholds were documented; no acceptance conclusion is inferred from these metrics.
- Dataset label provenance and deployment-domain representativeness remain unverified.

See test_metrics.json, per_class_report.csv, confusion_matrix.csv, and class_confusions.csv for detailed results.
