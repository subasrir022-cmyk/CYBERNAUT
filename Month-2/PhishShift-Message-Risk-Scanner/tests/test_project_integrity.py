from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def test_model_metrics_file_exists():
    assert (ROOT / "results" / "model_metrics.csv").exists()

def test_three_models_are_evaluated():
    metrics = pd.read_csv(ROOT / "results" / "model_metrics.csv")
    assert len(metrics) >= 3
    assert {"model", "accuracy", "precision", "recall", "f1",
            "false_positive_rate", "TN", "FP", "FN", "TP"}.issubset(metrics.columns)

def test_metrics_are_in_valid_ranges():
    metrics = pd.read_csv(ROOT / "results" / "model_metrics.csv")
    for col in ["accuracy", "precision", "recall", "f1", "false_positive_rate"]:
        assert metrics[col].between(0, 1).all(), f"Invalid values in {col}"

def test_report_and_documentation_exist():
    for relative_path in [
        "docs/REQUIREMENT_TRACKER.md",
        "docs/SRS.md",
        "docs/THREAT_MODEL.md",
        "docs/DEMO_SCRIPT.md",
        "docs/PhishShift_Final_Report.pdf",
    ]:
        assert (ROOT / relative_path).is_file(), f"Missing {relative_path}"

def test_app_does_not_fetch_user_supplied_urls():
    app = (ROOT / "app.py").read_text(encoding="utf-8").lower()
    assert "requests.get(" not in app
    assert "urllib.request.urlopen(" not in app
