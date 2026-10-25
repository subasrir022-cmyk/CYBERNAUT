from pathlib import Path
import json
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
DOCS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

metrics_path = RESULTS / "model_metrics.csv"
if not metrics_path.exists():
    raise FileNotFoundError("results/model_metrics.csv not found. Existing project results were not changed.")

metrics = pd.read_csv(metrics_path)
required = {"model", "accuracy", "precision", "recall", "f1", "false_positive_rate", "TN", "FP", "FN", "TP"}
if not required.issubset(metrics.columns):
    raise ValueError("Unexpected metrics CSV columns. No report generated.")

def pct(value):
    return f"{float(value) * 100:.2f}%"

best = metrics.sort_values("f1", ascending=False).iloc[0]
rows = []
for _, r in metrics.iterrows():
    rows.append({
        "model": str(r["model"]),
        "accuracy": float(r["accuracy"]),
        "precision": float(r["precision"]),
        "recall": float(r["recall"]),
        "f1": float(r["f1"]),
        "false_positive_rate": float(r["false_positive_rate"]),
        "TN": int(r["TN"]), "FP": int(r["FP"]),
        "FN": int(r["FN"]), "TP": int(r["TP"])
    })

# Requirements tracker: statuses are intentionally conservative.
tracker = """# PhishShift Requirement Tracker

Status meanings: Not Started / In Progress / Tested / Evidence Saved.

| ID | Requirement | Status | Evidence / limitation |
|---|---|---|---|
| R01 | At least 400 benign and suspicious messages | Tested | SMS Spam Collection contains 5,169 unique messages after exact deduplication; its spam class is not equivalent to phishing. |
| R02 | Record dataset sources and reuse terms | In Progress | See `data/data_manifest.csv`; NCSU dataset-specific terms still require confirmation. |
| R03 | Preserve raw records | In Progress | Raw files are present; verify checksums before claiming immutable preservation. |
| R04 | Sanitize/defang URLs and never open user links | In Progress | App text says links are not opened; add and test explicit defanging if required. |
| R05 | Rule-based baseline | Tested | Metrics in `results/model_metrics.csv`. |
| R06 | TF-IDF linear classifier | Tested | Logistic Regression metrics in `results/model_metrics.csv`. |
| R07 | Third ML approach | Tested | Multinomial Naive Bayes metrics in `results/model_metrics.csv`. |
| R08 | Exact duplicate removal | Tested | Training pipeline deduplicates exact message text. |
| R09 | Near-duplicate removal | Not Started | No verified near-duplicate filtering evidence yet. |
| R10 | Campaign-separated holdout | In Progress | Campaign mapping is unreliable; do not report campaign-independent performance. |
| R11 | Confusion analysis and false-positive rate | Tested | `results/confusion_matrices.json`, `results/model_metrics.csv`. |
| R12 | Three visualizations | In Progress | Verify all three expected image files exist and are readable. |
| R13 | Uncertainty/abstain behavior | In Progress | Must be implemented and tested in the app before claiming complete. |
| R14 | Automated acceptance and robustness tests | In Progress | Run `python -m pytest -q`; save actual output as evidence. |
| R15 | SRS and threat model | Evidence Saved | `SRS.md` and `THREAT_MODEL.md` in this folder. |
| R16 | Final report PDF | Evidence Saved | This PDF reports existing metrics and outstanding limitations. |
| R17 | Demo script | Evidence Saved | `DEMO_SCRIPT.md`. |
| R18 | Mentor's unseen campaign test | Not Started | Keep mentor-provided messages out of training; test only when received. |
"""
(DOCS / "REQUIREMENT_TRACKER.md").write_text(tracker, encoding="utf-8")

srs = """# Software Requirements Specification (SRS) — PhishShift

## 1. Purpose
PhishShift is an educational message-risk screening tool. It classifies SMS-like text as spam-like or ham-like and surfaces wording cues for manual review. It is not a definitive phishing detector.

## 2. Scope
- Accept pasted text in a Streamlit interface.
- Run a locally stored text-classification model.
- Display the model label and heuristic warning cues.
- Keep a temporary, session-only history of up to ten scans.
- Never fetch or open URLs contained in submitted messages.

## 3. Users
Students, demonstrators, and reviewers evaluating suspicious-message awareness.

## 4. Functional requirements
FR-01: Accept a text message up to the UI's configured character limit.
FR-02: Warn when the input is empty or the model is unavailable.
FR-03: Show a model classification and explain that a ham-like result is not a safety guarantee.
FR-04: Identify link, urgency, verification, account-pressure, sensitive-information, reward, and action-request cues.
FR-05: Show a heuristic signal index clearly labelled as not a probability.
FR-06: Keep scan history in Streamlit session state only and allow clearing it.
FR-07: Do not fetch URLs from submitted messages.
FR-08: Uncertain model outputs should be routed to manual review once a validated abstain threshold is implemented.

## 5. Non-functional requirements
- Run locally with Python, Streamlit, scikit-learn, joblib, pandas, and the listed dependencies.
- Handle model loading or prediction errors without crashing the interface.
- Explain limitations and avoid promising that messages are safe.
- Keep raw source data separate from processed training data.

## 6. Data and evaluation
Current metrics are based on a random, stratified ham/spam split. Spam is not synonymous with phishing. The campaign-separated holdout is not validated and must not be claimed as completed. NCSU extracted messages labelled unknown are not treated as supervised labels.

## 7. Acceptance criteria
- App launches and loads the saved model.
- Empty input is handled.
- A suspicious simulation produces a visible result and cue breakdown.
- A benign simulation produces a result without claiming guaranteed safety.
- User-provided URLs are not opened.
- Model metrics and limitations are documented.
- Abstain behavior and automated tests must pass before their status is marked complete.
"""
(DOCS / "SRS.md").write_text(srs, encoding="utf-8")

threat = """# PhishShift Threat Model

## Assets
- User-pasted message text and any private content in it.
- Local model files, source code, datasets, and evaluation results.
- Trustworthiness of the scanner's output.

## Trust boundaries
- Pasted text is untrusted input.
- Model prediction and regex cues are screening signals, not ground truth.
- Local project files are trusted only if obtained from expected project sources.

## Threats and mitigations
1. Malicious URL in a message: do not click, resolve, or fetch it; inspect text only.
2. Social-engineering language: display cues and recommend independent verification.
3. False negative: a ham-like prediction may still be malicious; never present it as guaranteed safe.
4. False positive: legitimate messages can be flagged; show the result as a model estimate.
5. Uncertain or unmapped model output: route to manual review when abstention is implemented.
6. Dataset label mismatch: SMS spam labels are not phishing labels; describe this limitation.
7. Data leakage: exact duplicates are removed, but near-duplicate and campaign-separated evaluation remain unverified.
8. Privacy exposure: scan history is session-only; avoid submitting passwords, OTPs, PINs, or private data.
9. Dependency or model tampering: install dependencies from the project's requirements and use trusted model artifacts.

## Residual risks
- Model performance may not generalize to modern phishing campaigns.
- Campaign-level independence has not been demonstrated.
- Heuristic cues can miss subtle attacks or flag legitimate messages.
- A risk index is not a calibrated phishing probability.
"""
(DOCS / "THREAT_MODEL.md").write_text(threat, encoding="utf-8")

demo = """# PhishShift Demo Script (3–5 minutes)

1. **Introduction (30 sec):** Explain that PhishShift is an educational message-risk screening tool, not a guarantee of safety.
2. **Dashboard (30 sec):** Show the loaded model status, session counters, and message input.
3. **Suspicious simulation (60 sec):** Select the simulated account-restriction message. Analyse it. Point out the model label, warning cues, and heuristic signal index. Do not open the URL.
4. **Ordinary simulation (45 sec):** Select the ordinary library-meeting message and analyse it. Explain that a ham-like result does not prove safety.
5. **Evaluation (45 sec):** Show `results/model_metrics.csv` and `results/confusion_matrix.png`. Explain that metrics come from a random ham/spam split, not a campaign-separated phishing benchmark.
6. **Limitations and safety (30 sec):** Mention potential false positives/negatives, unverified campaign mapping, and the need for independent sender verification.
7. **Close (10 sec):** Summarise that the tool supports review and awareness; it does not replace security controls.
"""
(DOCS / "DEMO_SCRIPT.md").write_text(demo, encoding="utf-8")

# Create a report using actual CSV values.
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="SmallNote", parent=styles["BodyText"], fontSize=8, leading=11))
story = [
    Paragraph("PhishShift: Message Risk Scanner", styles["Title"]),
    Paragraph("Project Evaluation Report", styles["Heading2"]),
    Spacer(1, 0.3 * cm),
    Paragraph("Purpose", styles["Heading2"]),
    Paragraph("PhishShift is an educational message-risk screening tool. It classifies SMS-like text and highlights warning cues. It is not a definitive phishing detector and does not open submitted URLs.", styles["BodyText"]),
    Spacer(1, 0.25 * cm),
    Paragraph("Evaluation scope", styles["Heading2"]),
    Paragraph("The metrics below are from the project's recorded random, stratified ham/spam test split. Spam labels are not equivalent to verified phishing labels. Campaign-separated evaluation remains incomplete because message-to-campaign mapping is not reliable.", styles["BodyText"]),
    Spacer(1, 0.25 * cm),
    Paragraph("Recorded model metrics", styles["Heading2"])
]
table_data = [["Model", "Accuracy", "Precision", "Recall", "F1", "FPR", "TN", "FP", "FN", "TP"]]
for r in rows:
    table_data.append([
        r["model"], pct(r["accuracy"]), pct(r["precision"]), pct(r["recall"]),
        pct(r["f1"]), pct(r["false_positive_rate"]),
        str(r["TN"]), str(r["FP"]), str(r["FN"]), str(r["TP"])
    ])
t = Table(table_data, repeatRows=1, colWidths=[3.2*cm,1.45*cm,1.45*cm,1.35*cm,1.2*cm,1.15*cm,0.8*cm,0.8*cm,0.8*cm,0.8*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#12304a")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("GRID", (0,0), (-1,-1), 0.35, colors.grey),
    ("FONTSIZE", (0,0), (-1,-1), 7),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef5fa")]),
]))
story.extend([t, Spacer(1, 0.25*cm)])
story.append(Paragraph(
    f"Highest recorded F1: {best['model']} (F1 {pct(best['f1'])}, accuracy {pct(best['accuracy'])}). "
    "These scores should not be interpreted as phishing-specific performance.",
    styles["BodyText"]))
story.extend([
    Spacer(1, 0.25*cm),
    Paragraph("Known limitations and outstanding work", styles["Heading2"]),
    Paragraph("Near-duplicate removal is not verified. Campaign-separated testing is not complete. The safe abstain/manual-review behavior must be implemented and tested before being marked complete. NCSU messages with unknown labels are not used as supervised training labels. Dataset-specific reuse terms should be confirmed before redistribution.", styles["BodyText"]),
    Spacer(1, 0.25*cm),
    Paragraph("Safety guidance", styles["Heading2"]),
    Paragraph("Never open a suspicious link to test it. Verify unexpected requests using an independently obtained official app, website, or phone number. Do not enter passwords, PINs, OTPs, or banking information into untrusted pages.", styles["BodyText"]),
    Spacer(1, 0.25*cm),
    Paragraph("Evidence files", styles["Heading2"]),
    Paragraph("Recorded metrics: results/model_metrics.csv; confusion matrices: results/confusion_matrices.json; evaluation summary: results/evaluation_summary.json; requirement tracker: docs/REQUIREMENT_TRACKER.md.", styles["SmallNote"])
])
pdf_path = DOCS / "PhishShift_Final_Report.pdf"
SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm).build(story)

print("Created documentation:")
for p in [DOCS/"REQUIREMENT_TRACKER.md", DOCS/"SRS.md", DOCS/"THREAT_MODEL.md", DOCS/"DEMO_SCRIPT.md", pdf_path]:
    print(f"- {p.relative_to(ROOT)} ({p.stat().st_size} bytes)")
print(f"\nMetrics rows included: {len(rows)}")
print(f"Best recorded F1 model: {best['model']} ({pct(best['f1'])})")
print("Note: no model, raw dataset, or app source file was overwritten.")
