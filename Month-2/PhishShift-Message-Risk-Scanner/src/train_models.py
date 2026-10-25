
from pathlib import Path
import json
import re
import joblib
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "sms_unique_messages.csv"
RESULTS = ROOT / "results"
MODELS = ROOT / "models"

RESULTS.mkdir(exist_ok=True)
MODELS.mkdir(exist_ok=True)


def rule_baseline(message):
    """Explainable spam-risk rules; not a phishing verdict."""
    text = str(message).lower()
    score = 0
    cues = []

    rules = [
        (r"https?://|www\.", 2, "contains a URL"),
        (
            r"\b(verify|confirm|restore|suspend|restricted)\b",
            2,
            "account verification or restriction wording",
        ),
        (
            r"\b(prize|winner|free|bonus|claim|cash)\b",
            1,
            "reward or money wording",
        ),
        (
            r"\b(urgent|immediately|act now|limited time)\b",
            1,
            "urgency wording",
        ),
        (
            r"\b(password|otp|pin|bank details)\b",
            2,
            "sensitive information wording",
        ),
    ]

    for pattern, points, cue in rules:
        if re.search(pattern, text):
            score += points
            cues.append(cue)

    return (
        int(score >= 2),
        "; ".join(cues) if cues else "no configured rule matched",
    )


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required = {"message_text", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required}")

    df = df.dropna(subset=["message_text", "label"]).copy()
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["message_text"] = df["message_text"].astype(str).str.strip()
    df = df[df["label"].isin(["ham", "spam"])]
    df = df[df["message_text"] != ""]
    df = df.drop_duplicates(subset=["message_text"]).reset_index(drop=True)

    if len(df) < 20 or df["label"].nunique() != 2:
        raise ValueError("Not enough labelled ham/spam messages to train.")

    # This dataset contains spam/ham labels, not verified phishing labels.
    X = df["message_text"]
    y = df["label"].map({"ham": 0, "spam": 1})

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    models = {
        "Rules baseline": None,
        "Multinomial Naive Bayes": Pipeline([
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    max_features=30000,
                ),
            ),
            ("model", MultinomialNB()),
        ]),
        "Logistic Regression": Pipeline([
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    max_features=30000,
                ),
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]),
    }

    rows = []
    confusion = {}

    for name, model in models.items():
        if model is None:
            predictions = X_test.apply(
                lambda message: rule_baseline(message)[0]
            ).astype(int)
        else:
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            safe_name = re.sub(
                r"[^a-z0-9]+", "_", name.lower()
            ).strip("_")
            joblib.dump(model, MODELS / f"{safe_name}.joblib")

        cm = confusion_matrix(y_test, predictions, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) else 0.0

        rows.append({
            "model": name,
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "f1": f1_score(y_test, predictions, zero_division=0),
            "false_positive_rate": fpr,
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp),
        })

        confusion[name] = cm.tolist()

    metrics = pd.DataFrame(rows)
    metrics.to_csv(RESULTS / "model_metrics.csv", index=False)

    with open(
        RESULTS / "confusion_matrices.json", "w", encoding="utf-8"
    ) as f:
        json.dump(confusion, f, indent=2)

    # Visualization 1: compare model metrics.
    metrics.set_index("model")[
        ["accuracy", "precision", "recall", "f1"]
    ].plot(kind="bar", ylim=(0, 1), figsize=(10, 6))

    plt.title("SMS Spam Model Comparison")
    plt.ylabel("Score")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(RESULTS / "model_comparison.png", dpi=150)
    plt.close()

    # Visualization 2: confusion matrix for the best F1 model.
    best_name = metrics.sort_values(
        "f1", ascending=False
    ).iloc[0]["model"]

    best_cm = np.array(confusion[best_name])

    disp = ConfusionMatrixDisplay(
        confusion_matrix=best_cm,
        display_labels=["ham", "spam"],
    )
    disp.plot()

    plt.title(f"Confusion Matrix - {best_name}")
    plt.tight_layout()
    plt.savefig(RESULTS / "confusion_matrix.png", dpi=150)
    plt.close()

    # Visualization 3: common terms in spam-labelled training messages.
    spam_text = X_train[y_train == 1]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_features=100,
    )
    matrix = vectorizer.fit_transform(spam_text)
    terms = vectorizer.get_feature_names_out()
    scores = matrix.mean(axis=0).A1

    keyword_df = pd.DataFrame({
        "keyword": terms,
        "mean_tfidf": scores,
    })
    keyword_df = keyword_df.sort_values(
        "mean_tfidf", ascending=False
    ).head(20)

    keyword_df.to_csv(
        RESULTS / "spam_keyword_summary.csv", index=False
    )

    keyword_df.sort_values("mean_tfidf").plot(
        x="keyword",
        y="mean_tfidf",
        kind="barh",
        legend=False,
        figsize=(9, 7),
    )

    plt.title("Frequent Terms in Spam-Labeled Training Messages")
    plt.xlabel("Mean TF-IDF")
    plt.tight_layout()
    plt.savefig(RESULTS / "spam_keywords.png", dpi=150)
    plt.close()

    summary = {
        "dataset": "UCI SMS Spam Collection",
        "task": "ham vs spam SMS classification; not verified phishing detection",
        "total_unique_messages": int(len(df)),
        "training_messages": int(len(X_train)),
        "test_messages": int(len(X_test)),
        "label_mapping": {"ham": 0, "spam": 1},
        "split": "stratified random split; campaign-separated testing not implemented",
        "best_by_f1": str(best_name),
        "limitations": [
            "UCI spam labels do not mean all spam messages are phishing.",
            "Random split is not campaign-separated evaluation.",
            "Rules are a simple baseline and may produce false positives.",
            "NCSU records with unknown labels were not used for supervised training.",
        ],
    }

    with open(
        RESULTS / "evaluation_summary.json", "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    print("\nTraining and evaluation completed.")
    print(metrics.round(4).to_string(index=False))
    print(f"\nBest by F1: {best_name}")
    print(f"Results saved in: {RESULTS}")
    print(f"Models saved in: {MODELS}")


if __name__ == "__main__":
    main()
