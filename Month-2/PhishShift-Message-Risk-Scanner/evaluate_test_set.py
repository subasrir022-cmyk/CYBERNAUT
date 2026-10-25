
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed" / "sms_unique_messages.csv"
MODEL_FILE = ROOT / "models" / "logistic_regression.joblib"
OUTPUT_FILE = ROOT / "results" / "test_set_predictions.csv"
SUMMARY_FILE = ROOT / "results" / "full_test_evaluation.json"


def main():
    df = pd.read_csv(DATA_FILE)
    df = df.dropna(subset=["message_text", "label"]).copy()
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["message_text"] = df["message_text"].astype(str).str.strip()
    df = df[df["label"].isin(["ham", "spam"])]
    df = df[df["message_text"] != ""]
    df = df.drop_duplicates(subset=["message_text"]).reset_index(drop=True)

    X = df["message_text"]
    y = df["label"].map({"ham": 0, "spam": 1})

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(MODEL_FILE)
    predictions = model.predict(X_test)

    results = pd.DataFrame({
        "message": X_test.to_numpy(),
        "actual_label": y_test.map({0: "ham", 1: "spam"}).to_numpy(),
        "predicted_label": pd.Series(predictions, index=X_test.index)
            .map({0: "ham", 1: "spam"}).to_numpy(),
    })
    results["correct"] = (
        results["actual_label"] == results["predicted_label"]
    )

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    results.to_csv(OUTPUT_FILE, index=False)

    cm = confusion_matrix(y_test, predictions, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    summary = {
        "dataset": "UCI SMS Spam Collection",
        "test_messages": int(len(results)),
        "correct_predictions": int(results["correct"].sum()),
        "incorrect_predictions": int((~results["correct"]).sum()),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_spam": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall_spam": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_spam": float(f1_score(y_test, predictions, zero_division=0)),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "classification_report": classification_report(
            y_test, predictions, target_names=["ham", "spam"],
            zero_division=0, output_dict=True
        ),
        "note": (
            "This evaluates ham/spam SMS classification, not verified "
            "phishing detection. It uses the existing random test split."
        ),
    }

    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("Full test-set evaluation completed.")
    print(f"Test messages: {len(results)}")
    print(f"Correct: {results['correct'].sum()}")
    print(f"Incorrect: {(~results['correct']).sum()}")
    print(f"Accuracy: {summary['accuracy']:.2%}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")
    print(f"All predictions saved to: {OUTPUT_FILE}")
    print(f"Summary saved to: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
