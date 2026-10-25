import pandas as pd
from src.near_duplicates import remove_near_duplicate_rows


def test_removes_similar_messages_with_same_label():
    df = pd.DataFrame({
        "message_text": [
            "Congratulations! You won a free prize today",
            "Congratulations! You won a free prize today!",
            "I will meet you at the library at four",
        ],
        "label": ["spam", "spam", "ham"],
    })

    cleaned, conflicts = remove_near_duplicate_rows(df)

    assert len(cleaned) == 2
    assert conflicts == []


def test_preserves_similar_messages_with_conflicting_labels():
    df = pd.DataFrame({
        "message_text": [
            "Congratulations! You won a free prize today",
            "Congratulations! You won a free prize today!",
        ],
        "label": ["spam", "ham"],
    })

    cleaned, conflicts = remove_near_duplicate_rows(df)

    assert len(cleaned) == 2
    assert len(conflicts) == 1


def test_keeps_unrelated_messages():
    df = pd.DataFrame({
        "message_text": [
            "Your bank account needs verification",
            "I will meet you at the library",
        ],
        "label": ["spam", "ham"],
    })

    cleaned, conflicts = remove_near_duplicate_rows(df)

    assert len(cleaned) == 2
    assert conflicts == []


def test_empty_dataframe():
    df = pd.DataFrame(columns=["message_text", "label"])

    cleaned, conflicts = remove_near_duplicate_rows(df)

    assert len(cleaned) == 0
    assert conflicts == []
