import pandas as pd
from collections import Counter
import re

# Load analyzed reviews
df = pd.read_csv("data/analyzed_reviews.csv")

# Combine all reviews
all_reviews = " ".join(df["review"].astype(str))

# Convert to lowercase
all_reviews = all_reviews.lower()

# Extract words
words = re.findall(r'\b[a-zA-Z]{3,}\b', all_reviews)

# Common words to ignore
stop_words = {
    "the", "and", "for", "are", "this", "that",
    "with", "very", "these", "they", "from",
    "product", "really", "after", "working",
    "worth", "money"
}

# Remove common words
filtered_words = [
    word for word in words
    if word not in stop_words
]

# Count words
word_counts = Counter(filtered_words)

# Display top 10 words
print("======================================")
print("TOP WORDS IN CUSTOMER REVIEWS")
print("======================================")

for word, count in word_counts.most_common(10):
    print(f"{word}: {count}")