
import pandas as pd
import pickle
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# 1. Load dataset
df = pd.read_csv(
    "data/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

X = df["message"]
y = df["label"].map({"ham": 0, "spam": 1})

# 2. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 3. Convert text into numerical features
tfidf = TfidfVectorizer(
    stop_words="english",
    lowercase=True
)

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# 4. Train SVM with probability calibration
base_model = LinearSVC()
model = CalibratedClassifierCV(base_model, cv=3)
model.fit(X_train_tfidf, y_train)

# 5. Evaluate model
predictions = model.predict(X_test_tfidf)

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

print("\nSPAM CLASSIFIER MODEL RESULTS")
print("-" * 40)
print(f"Accuracy : {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall   : {recall * 100:.2f}%")
print(f"F1 Score : {f1 * 100:.2f}%")

# 6. Save model and vectorizer
Path("models").mkdir(exist_ok=True)

with open("models/spam_model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("models/tfidf_vectorizer.pkl", "wb") as file:
    pickle.dump(tfidf, file)

print("\nModel saved successfully!")
print("Files saved in the models folder.")