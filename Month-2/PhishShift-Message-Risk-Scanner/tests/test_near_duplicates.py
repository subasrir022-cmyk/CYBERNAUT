from src.train_models import remove_near_duplicates


def test_removes_near_duplicate_messages():
    messages = [
        "Congratulations! You won a free prize today",
        "Congratulations! You won a free prize today!",
        "I will meet you at the library at four",
    ]

    cleaned = remove_near_duplicates(messages)

    assert len(cleaned) == 2


def test_keeps_unrelated_messages():
    messages = [
        "Your bank account needs verification",
        "I will meet you at the library",
    ]

    cleaned = remove_near_duplicates(messages)

    assert len(cleaned) == 2


def test_empty_input():
    assert remove_near_duplicates([]) == []