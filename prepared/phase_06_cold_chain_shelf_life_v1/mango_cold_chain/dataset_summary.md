# Mango cold-chain measurements

**Readiness: AUDIT_COMPLETE**

Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\cold_chain\mango_shipment`. The inventory contains 563 files across raw measurement, processed result, documentation, R code, and photo/device folders. Parsed 367 raw and processed tabular files into 47353 traceable records. Found 20665 exact box/time/value overlaps across files and 0 conflicting box/time keys. Raw measurement tables contain 774 blank/NA cells and 1 invalid/width findings; the color sources include a questionable L_D12 value 69/21. The README count differs from disk: 342 vs 341 T/H data files and 19 vs 17 W/C/pH/TSS data tables (21 files when including 4 read.me documents). The README documents 5-minute iButton temperature readings, °C and %RH, and quality measurements across D0–D15 under 16°C/21°C conditions.

Per-file rows, timestamps, intervals, and ranges are in `data_quality_report.json`; source names, sizes, formats, hashes and schemas are in `source_file_inventory.csv`. Quality and sensor records were not merged: box/configuration associations are plausible at batch level, but a verified physical-sample and timestamp crosswalk for a leakage-safe supervised target was not established. The measured mass/color/pH/TSS trajectories do not define a remaining-shelf-life endpoint. No cleaned or split data was created.
