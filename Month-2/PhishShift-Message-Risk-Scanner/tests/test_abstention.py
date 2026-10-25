def classify_confidence(confidence, threshold=0.65):
    if confidence is None or confidence < threshold:
        return "NEEDS REVIEW"
    return "CLASSIFIED"


def test_low_confidence_needs_review():
    assert classify_confidence(0.40) == "NEEDS REVIEW"


def test_confidence_below_threshold_needs_review():
    assert classify_confidence(0.64) == "NEEDS REVIEW"


def test_confidence_at_threshold_is_classified():
    assert classify_confidence(0.65) == "CLASSIFIED"


def test_high_confidence_is_classified():
    assert classify_confidence(0.90) == "CLASSIFIED"


def test_missing_confidence_needs_review():
    assert classify_confidence(None) == "NEEDS REVIEW"