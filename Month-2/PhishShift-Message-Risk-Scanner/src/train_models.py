
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

from src.near_duplicates import remove_near_duplicate_rows


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "sms_unique_messages.csv"
RESULTS = ROOT / "results"
MODELS = ROOT / "models"

RESULTS.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)


def remove_near_duplicates(messages, threshold=0.92):
    """Remove near-duplicate messages while preserving the first occurrence."""
    from difflib import SequenceMatcher

    cleaned = []
    normalized_messages = []

    for message in messages:
        original = str(message).strip()
        normalized = re.sub(r"\s+", " ", original.lower())
        normalized = re.sub(r"[^\w\s]", "", normalized)

        if not normalized:
            continue

        if any(
            SequenceMatcher(None, normalized, old).ratio() >= threshold
            for old in normalized_messages
        ):
            continue

        cleaned.append(original)
        normalized_messages.append(normalized)

    return cleaned
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

    return int(score >= 2), (
        "; ".join(cues) if cues else "no configured rule matched"
    )


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required = {"message_text", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required}")

    # Basic cleaning and label validation.
    df = df.dropna(subset=["message_text", "label"]).copy()
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["message_text"] = df["message_text"].astype(str).str.strip()

    df = df[df["label"].isin(["ham", "spam"])]
    df = df[df["message_text"] != ""]

    # Remove exact duplicates while preserving each message's label.
    df = df.drop_duplicates(
        subset=["message_text"], keep="first"
    ).reset_index(drop=True)

    messages_after_exact_dedup = len(df)

    if len(df) < 20 or df["label"].nunique() != 2:
        raise ValueError(
            "Not enough labelled ham/spam messages to train."
        )

    # Keep the original labelled rows so conflict indexes can be reviewed.
    original_df = df.copy()

    # Remove near-duplicates only when their labels match.
    # Messages with conflicting labels are retained and flagged for review.
    df, conflicting_pairs = remove_near_duplicate_rows(
        df, threshold=0.92
    )

    df = df.reset_index(drop=True)
    messages_after_near_dedup = len(df)

    near_duplicates_removed = (
        messages_after_exact_dedup - messages_after_near_dedup
    )

    print(
        f"Messages before near-duplicate removal: "
        f"{messages_after_exact_dedup}"
    )
    print(
        f"Messages after near-duplicate removal: "
        f"{messages_after_near_dedup}"
    )
    print(
        f"Conflicting-label pairs flagged for review: "
        f"{len(conflicting_pairs)}"
    )

    # Save potentially conflicting near-duplicate pairs for manual review.
    conflict_rows = []

    for first_idx, second_idx in conflicting_pairs:
        first = original_df.iloc[first_idx]
        second = original_df.iloc[second_idx]

        conflict_rows.append({
            "message_1": first["message_text"],
            "label_1": first["label"],
            "message_2": second["message_text"],
            "label_2": second["label"],
            "similarity_threshold": 0.92,
            "review_status": "needs manual review",
        })

    conflict_file = RESULTS / "near_duplicate_label_conflicts.csv"

    pd.DataFrame(
        conflict_rows,
        columns=[
            "message_1",
            "label_1",
            "message_2",
            "label_2",
            "similarity_threshold",
            "review_status",
        ],
    ).to_csv(conflict_file, index=False)

    if len(df) < 20 or df["label"].nunique() != 2:
        raise ValueError(
            "Not enough labelled ham/spam messages after "
            "near-duplicate removal."
        )

    # The dataset has ham/spam labels, not verified phishing labels.
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
            "f1": f1_score(
                y_test, predictions, zero_division=0
            ),
            "false_positive_rate": fpr,
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp),
        })

        confusion[name] = cm.tolist()

    # Save model metrics and confusion matrices.
    metrics = pd.DataFrame(rows)
    metrics.to_csv(RESULTS / "model_metrics.csv", index=False)

    with open(
        RESULTS / "confusion_matrices.json",
        "w",
        encoding="utf-8",
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
    }).sort_values(
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

    # Save a summary of the evaluation and dataset limitations.
    summary = {
        "dataset": "UCI SMS Spam Collection",
        "task": (
            "ham vs spam SMS classification; "
            "not verified phishing detection"
        ),
        "total_unique_messages": int(len(df)),
        "messages_after_exact_dedup": int(messages_after_exact_dedup),
        "messages_after_near_dedup": int(messages_after_near_dedup),
        "near_duplicates_removed": int(near_duplicates_removed),
        "near_duplicate_similarity_threshold": 0.92,
        "conflicting_label_pairs_flagged": len(conflicting_pairs),
        "conflicting_label_report": str(
            conflict_file.relative_to(ROOT)
        ),
        "training_messages": int(len(X_train)),
        "test_messages": int(len(X_test)),
        "label_mapping": {"ham": 0, "spam": 1},
        "split": (
            "stratified random split; "
            "campaign-separated testing not implemented"
        ),
        "best_by_f1": str(best_name),
        "limitations": [
            "UCI spam labels do not mean all spam messages are phishing.",
            "Random split is not campaign-separated evaluation.",
            (
                "Near-duplicate matching uses character n-gram "
                "similarity; review conflicting labels manually."
            ),
            "Rules are a simple baseline and may produce false positives.",
            "Records with unknown labels are not used for supervised training.",
        ],
    }

    with open(
        RESULTS / "evaluation_summary.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(summary, f, indent=2)

    print("\nTraining and evaluation completed.")
    print(metrics.round(4).to_string(index=False))
    print(f"\nBest by F1: {best_name}")
    print(
        f"Messages after exact deduplication: "
        f"{messages_after_exact_dedup}"
    )
    print(
        f"Messages after near-deduplication: "
        f"{messages_after_near_dedup}"
    )
    print(f"Near-duplicates removed: {near_duplicates_removed}")
    print(f"Conflicting-label pairs flagged: {len(conflicting_pairs)}")
    print(f"Conflict review report: {conflict_file}")
    print(f"Results saved in: {RESULTS}")
    print(f"Models saved in: {MODELS}")


if __name__ == "__main__":
    main()
