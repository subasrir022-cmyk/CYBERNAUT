
import json
import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns

from nltk.stem import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# --------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "SMSSpamCollection"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
stemmer = PorterStemmer()

# --------------------------------------------------
# 2. TEXT PREPROCESSING USING NLTK
# --------------------------------------------------

def clean_text(text):
    text = str(text).lower()
    words = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text)

    cleaned_words = []

    for word in words:
        if word.isalpha() and len(word) > 2:
            word = stemmer.stem(word)
        cleaned_words.append(word)

    return " ".join(cleaned_words)


# --------------------------------------------------
# 3. LOAD AND VALIDATE DATASET
# --------------------------------------------------

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}"
    )

df = pd.read_csv(
    DATA_PATH,
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

df = df.dropna(subset=["label", "message"])
df["label"] = df["label"].str.strip().str.lower()
df = df[df["label"].isin(["ham", "spam"])].copy()

df["target"] = df["label"].map({"ham": 0, "spam": 1})
df["message"] = df["message"].astype(str)

if df["target"].nunique() != 2:
    raise ValueError("Dataset must contain both ham and spam messages.")

print("\nEMAIL SPAM CLASSIFIER - MODEL TRAINING")
print("=" * 55)
print(f"Total messages: {len(df)}")
print(f"Ham messages : {(df['target'] == 0).sum()}")
print(f"Spam messages: {(df['target'] == 1).sum()}")

# --------------------------------------------------
# 4. SPLIT DATA BEFORE LEARNING VOCABULARY
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    df["message"],
    df["target"],
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=df["target"]
)

vectorizer = TfidfVectorizer(
    preprocessor=clean_text,
    lowercase=False,
    ngram_range=(1, 2),
    max_features=30000,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"\nTraining messages: {len(X_train)}")
print(f"Testing messages : {len(X_test)}")
print(f"TF-IDF features  : {X_train_tfidf.shape[1]}")

# --------------------------------------------------
# 5. TRAIN AND COMPARE THREE MODELS
# --------------------------------------------------

models = {
    "Multinomial Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(
        max_iter=1500,
        random_state=RANDOM_STATE
    ),
    "Calibrated Linear SVM": CalibratedClassifierCV(
        estimator=LinearSVC(random_state=RANDOM_STATE),
        cv=3
    )
}

results = []
trained_models = {}
predictions_by_model = {}

for model_name, candidate in models.items():
    print(f"\nTraining: {model_name} ...")

    candidate.fit(X_train_tfidf, y_train)
    predictions = candidate.predict(X_test_tfidf)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "False Positive Rate": false_positive_rate,
        "True Negative": int(tn),
        "False Positive": int(fp),
        "False Negative": int(fn),
        "True Positive": int(tp)
    })

    trained_models[model_name] = candidate
    predictions_by_model[model_name] = predictions

# Prefer models with recall >= 70%, when available.
eligible = [
    result for result in results
    if result["Recall"] >= 0.70
]

selection_pool = eligible if eligible else results

# Select by F1 first, then precision, then lower false-positive rate.
best_result = max(
    selection_pool,
    key=lambda item: (
        item["F1 Score"],
        item["Precision"],
        -item["False Positive Rate"]
    )
)

best_name = best_result["Model"]
best_model = trained_models[best_name]
best_predictions = predictions_by_model[best_name]

results_df = pd.DataFrame(results).sort_values(
    by="F1 Score", ascending=False
)

results_df.to_csv(
    MODEL_DIR / "model_metrics.csv",
    index=False
)

print("\nMODEL COMPARISON")
print("=" * 75)
print(results_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\nSelected model: {best_name}")

# --------------------------------------------------
# 6. SAVE SELECTED MODEL AND VECTORIZER
# --------------------------------------------------

with open(MODEL_DIR / "spam_model.pkl", "wb") as file:
    pickle.dump(best_model, file)

with open(MODEL_DIR / "tfidf_vectorizer.pkl", "wb") as file:
    pickle.dump(vectorizer, file)

# --------------------------------------------------
# 7. SAVE EVALUATION REPORT
# --------------------------------------------------

tn, fp, fn, tp = confusion_matrix(
    y_test, best_predictions, labels=[0, 1]
).ravel()

best_metrics = {
    "selected_model": best_name,
    "test_samples": int(len(y_test)),
    "accuracy": float(accuracy_score(y_test, best_predictions)),
    "precision": float(precision_score(
        y_test, best_predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y_test, best_predictions, zero_division=0
    )),
    "f1_score": float(f1_score(
        y_test, best_predictions, zero_division=0
    )),
    "false_positive_rate": float(
        fp / (fp + tn) if (fp + tn) else 0.0
    ),
    "true_negative": int(tn),
    "false_positive": int(fp),
    "false_negative": int(fn),
    "true_positive": int(tp)
}

with open(MODEL_DIR / "evaluation_summary.json", "w", encoding="utf-8") as file:
    json.dump(best_metrics, file, indent=4)

with open(MODEL_DIR / "confusion_matrices.json", "w", encoding="utf-8") as file:
    json.dump({
        name: confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ).tolist()
        for name, predictions in predictions_by_model.items()
    }, file, indent=4)

print("\nSELECTED MODEL TEST REPORT")
print("=" * 55)
print(classification_report(
    y_test,
    best_predictions,
    labels=[0, 1],
    target_names=["HAM", "SPAM"],
    zero_division=0
))
print(f"False-positive rate: {best_metrics['false_positive_rate'] * 100:.2f}%")

# --------------------------------------------------
# 8. CONFUSION MATRIX VISUALIZATION
# --------------------------------------------------

matrix = confusion_matrix(
    y_test, best_predictions, labels=[0, 1]
)

plt.figure(figsize=(7, 5))
sns.heatmap(
    matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["HAM", "SPAM"],
    yticklabels=["HAM", "SPAM"]
)
plt.title(f"Confusion Matrix - {best_name}")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.tight_layout()
plt.savefig(
    MODEL_DIR / "confusion_matrix.png",
    dpi=160
)
plt.close()

# --------------------------------------------------
# 9. SPAM-INDICATING KEYWORDS
# --------------------------------------------------

spam_messages = X_train[y_train == 1]
ham_messages = X_train[y_train == 0]

spam_tfidf = vectorizer.transform(spam_messages)
ham_tfidf = vectorizer.transform(ham_messages)

spam_mean = np.asarray(spam_tfidf.mean(axis=0)).ravel()
ham_mean = np.asarray(ham_tfidf.mean(axis=0)).ravel()

feature_names = np.array(vectorizer.get_feature_names_out())
difference = spam_mean - ham_mean

keyword_df = pd.DataFrame({
    "keyword": feature_names,
    "spam_tfidf_mean": spam_mean,
    "ham_tfidf_mean": ham_mean,
    "spam_association_score": difference
})

keyword_df = keyword_df.sort_values(
    "spam_association_score",
    ascending=False
)

keyword_df.to_csv(
    MODEL_DIR / "spam_keywords.csv",
    index=False
)

top_keywords = keyword_df.head(15).sort_values(
    "spam_association_score"
)

plt.figure(figsize=(10, 7))
sns.barplot(
    data=top_keywords,
    x="spam_association_score",
    y="keyword"
)
plt.title("Words More Associated with Spam Messages")
plt.xlabel("Mean TF-IDF Difference (Spam minus HAM)")
plt.ylabel("Word or Phrase")
plt.tight_layout()
plt.savefig(
    MODEL_DIR / "spam_keywords.png",
    dpi=160
)
plt.close()

# --------------------------------------------------
# 10. MODEL COMPARISON CHART
# --------------------------------------------------

chart_df = results_df.melt(
    id_vars="Model",
    value_vars=["Accuracy", "Precision", "Recall", "F1 Score"],
    var_name="Metric",
    value_name="Score"
)

plt.figure(figsize=(11, 6))
sns.barplot(
    data=chart_df,
    x="Model",
    y="Score",
    hue="Metric"
)
plt.ylim(0, 1)
plt.title("Machine Learning Model Comparison")
plt.xticks(rotation=12)
plt.tight_layout()
plt.savefig(
    MODEL_DIR / "model_comparison.png",
    dpi=160
)
plt.close()

print("\nTRAINING COMPLETE!")
print("-" * 55)
print("Saved model files:")
print("  models/spam_model.pkl")
print("  models/tfidf_vectorizer.pkl")
print("Saved evaluation files:")
print("  models/model_metrics.csv")
print("  models/evaluation_summary.json")
print("  models/confusion_matrices.json")
print("Saved visualizations:")
print("  models/confusion_matrix.png")
print("  models/spam_keywords.png")
print("  models/model_comparison.png")
print("Saved keyword data:")
print("  models/spam_keywords.csv")
print("\nNote: The dataset contains SMS messages, not real inbox emails.")
print("Keyword association does not prove that a word is always spam.")