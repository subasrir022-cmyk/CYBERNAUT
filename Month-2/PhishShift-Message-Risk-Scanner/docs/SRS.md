# Software Requirements Specification (SRS) — PhishShift

## 1. Purpose
PhishShift is an educational message-risk screening tool. It classifies SMS-like text as spam-like or ham-like and surfaces wording cues for manual review. It is not a definitive phishing detector.

## 2. Scope
- Accept pasted text in a Streamlit interface.
- Run a locally stored text-classification model.
- Display the model label and heuristic warning cues.
- Keep a temporary, session-only history of up to ten scans.
- Never fetch or open URLs contained in submitted messages.

## 3. Users
Students, demonstrators, and reviewers evaluating suspicious-message awareness.

## 4. Functional requirements
FR-01: Accept a text message up to the UI's configured character limit.
FR-02: Warn when the input is empty or the model is unavailable.
FR-03: Show a model classification and explain that a ham-like result is not a safety guarantee.
FR-04: Identify link, urgency, verification, account-pressure, sensitive-information, reward, and action-request cues.
FR-05: Show a heuristic signal index clearly labelled as not a probability.
FR-06: Keep scan history in Streamlit session state only and allow clearing it.
FR-07: Do not fetch URLs from submitted messages.
FR-08: Uncertain model outputs should be routed to manual review once a validated abstain threshold is implemented.

## 5. Non-functional requirements
- Run locally with Python, Streamlit, scikit-learn, joblib, pandas, and the listed dependencies.
- Handle model loading or prediction errors without crashing the interface.
- Explain limitations and avoid promising that messages are safe.
- Keep raw source data separate from processed training data.

## 6. Data and evaluation
Current metrics are based on a random, stratified ham/spam split. Spam is not synonymous with phishing. The campaign-separated holdout is not validated and must not be claimed as completed. NCSU extracted messages labelled unknown are not treated as supervised labels.

## 7. Acceptance criteria
- App launches and loads the saved model.
- Empty input is handled.
- A suspicious simulation produces a visible result and cue breakdown.
- A benign simulation produces a result without claiming guaranteed safety.
- User-provided URLs are not opened.
- Model metrics and limitations are documented.
- Abstain behavior and automated tests must pass before their status is marked complete.
