# PhishShift Requirement Tracker

Status meanings: Not Started / In Progress / Tested / Evidence Saved.

| ID | Requirement | Status | Evidence / limitation |
|---|---|---|---|
| R01 | At least 400 benign and suspicious messages | Tested | SMS Spam Collection contains 5,169 unique messages after exact deduplication; its spam class is not equivalent to phishing. |
| R02 | Record dataset sources and reuse terms | In Progress | See `data/data_manifest.csv`; NCSU dataset-specific terms still require confirmation. |
| R03 | Preserve raw records | In Progress | Four files in `data/raw/` are present. Current SHA-256 hashes saved in `results/raw_data_checksums.csv`; original-download checksums are unavailable, so unchanged-from-source integrity is not independently verified. |
| R04 | Sanitize/defang URLs and never open user links | In Progress | App text says links are not opened; add and test explicit defanging if required. |
| R05 | Rule-based baseline | Tested | Metrics in `results/model_metrics.csv`. |
| R06 | TF-IDF linear classifier | Tested | Logistic Regression metrics in `results/model_metrics.csv`. |
| R07 | Third ML approach | Tested | Multinomial Naive Bayes metrics in `results/model_metrics.csv`. |
| R08 | Exact duplicate removal | Tested | Training pipeline deduplicates exact message text. |
| R09 | Near-duplicate removal | Not Started | No verified near-duplicate filtering evidence yet. |
| R10 | Campaign-separated holdout | In Progress | Campaign mapping is unreliable; do not report campaign-independent performance. |
| R11 | Confusion analysis and false-positive rate | Tested | `results/confusion_matrices.json`, `results/model_metrics.csv`. |
| R12 | Three visualizations | Tested | Three PNG files exist, have non-zero sizes, pass Pillow image loading, and open successfully; chart labels and values still need visual review. Files: `results/confusion_matrix.png`, `results/model_comparison.png`, `results/spam_keywords.png`. |
| R13 | Uncertainty/abstain behavior | Tested | Confidence below 65% or unavailable leads to NEEDS REVIEW; app manually tested and 10 automated tests passed. Evidence: `results/pytest_output.txt`.
| R14 | Automated acceptance and robustness tests | In Progress | `python -m pytest -q` passed 10 existing tests; output saved in `results/pytest_output.txt`. Broader assignment-specific robustness and acceptance coverage remains to be verified. |
| R15 | SRS and threat model | Evidence Saved | `SRS.md` and `THREAT_MODEL.md` in this folder. |
| R16 | Final report PDF | Evidence Saved | This PDF reports existing metrics and outstanding limitations. |
| R17 | Demo script | Evidence Saved | `DEMO_SCRIPT.md`. |
| R18 | Mentor's unseen campaign test | Not Started | Keep mentor-provided messages out of training; test only when received. |



