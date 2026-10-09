
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
df = pd.read_csv(
    "data/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

# Convert labels into numbers
df["label"] = df["label"].map({"ham": 0, "spam": 1})

# Separate messages and labels
X = df["message"]
y = df["label"]

# Convert text into numerical features
tfidf = TfidfVectorizer(stop_words="english", lowercase=True)
X_tfidf = tfidf.fit_transform(X)

# Split dataset into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("TEXT PREPROCESSING COMPLETED!")
print("Total messages:", len(df))
print("TF-IDF feature shape:", X_tfidf.shape)
print("Training messages:", X_train.shape[0])
print("Testing messages:", X_test.shape[0])
print("Spam label: 1")
print("Ham label: 0")