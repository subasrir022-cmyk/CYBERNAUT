import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


def remove_near_duplicate_rows(df, threshold=0.92):
    """Remove highly similar messages with matching labels.

    Similar messages with conflicting labels are preserved for review.
    Returns (cleaned_dataframe, conflicting_pairs).
    """
    required = {"message_text", "label"}
    if not required.issubset(df.columns):
        raise ValueError("DataFrame must contain message_text and label columns.")
    if not 0 < threshold <= 1:
        raise ValueError("threshold must be greater than 0 and at most 1.")

    result = df.copy().reset_index(drop=True)
    result["_normalized"] = (
        result["message_text"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    valid = result["_normalized"].ne("")
    working = result.loc[valid].copy()
    if len(working) < 2:
        return result.drop(columns="_normalized"), []

    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=False)
    matrix = vectorizer.fit_transform(working["_normalized"])

    neighbors = NearestNeighbors(metric="cosine", algorithm="brute", n_jobs=-1)
    neighbors.fit(matrix)
    distances, indices = neighbors.radius_neighbors(
        matrix, radius=1 - threshold, return_distance=True
    )

    labels = working["label"].astype(str).str.lower().str.strip().tolist()
    original_indices = working.index.tolist()
    removed = set()
    conflicting_pairs = []

    for i, (row_distances, row_neighbors) in enumerate(zip(distances, indices)):
        if i in removed:
            continue
        for distance, j in sorted(zip(row_distances, row_neighbors), key=lambda pair: pair[0]):
            j = int(j)
            if i == j or j in removed:
                continue
            if labels[i] == labels[j]:
                removed.add(j)
            else:
                pair = (original_indices[i], original_indices[j])
                reverse_pair = (pair[1], pair[0])
                if pair not in conflicting_pairs and reverse_pair not in conflicting_pairs:
                    conflicting_pairs.append(pair)

    cleaned = result.drop(index=[original_indices[i] for i in removed])
    cleaned = cleaned.drop(columns="_normalized").reset_index(drop=True)
    return cleaned, conflicting_pairs
