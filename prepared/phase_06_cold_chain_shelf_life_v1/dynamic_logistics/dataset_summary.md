# Dynamic logistics dataset

**Readiness: BLOCKED for supervised cold-chain shipment-risk prediction.**

Source: `C:\Users\nirma\OneDrive\Desktop\logistic\datasets\dynamic_supply_chain_logistics_dataset.csv`. No local schema/readme was located alongside the CSV. The data has 32065 rows and 26 columns. It contains 32,065 unique timestamps exactly one hour apart from 2021-01-01 through 2024-08-29, no missing values and no exact duplicate rows. Risk labels are High 23,944, Moderate 5,011, Low 3,110. Candidate `delay_probability` spans nearly 0–1 inside every risk class, so the class does not map cleanly to that field; target-generation rules, row unit, prediction time, feature timing, units and provenance are undocumented. No shipment/trip/vehicle identifiers support group-based validation. `delivery_time_deviation` and multiple operational fields may reveal post-event outcomes. No cleaned output or split was created.
