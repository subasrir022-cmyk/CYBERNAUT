
import pickle
import json
import email
from email import policy
from pathlib import Path

import pandas as pd
import streamlit as st
import re
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def clean_text(text):
    text = str(text).lower()
    words = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text)

    cleaned_words = []

    for word in words:
        if word.isalpha() and len(word) > 2:
            word = stemmer.stem(word)
        cleaned_words.append(word)

    return " ".join(cleaned_words)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

st.set_page_config(
    page_title="Email Spam Classifier",
    page_icon="📧",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #F1F5F9;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #7DD3FC !important;
}
div[data-testid="stTextArea"] textarea {
    background: #111C30;
    color: white;
    border: 1px solid #33445F;
    border-radius: 12px;
}
div.stButton > button {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 44px;
    font-weight: bold;
}
.metric-card {
    background: #111C30;
    border: 1px solid #33445F;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 8px;
}
.small-note {
    color: #A7B5CC;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    with open(MODEL_DIR / "spam_model.pkl", "rb") as file:
        model = pickle.load(file)

    with open(MODEL_DIR / "tfidf_vectorizer.pkl", "rb") as file:
        vectorizer = pickle.load(file)

    return model, vectorizer


def extract_eml_text(uploaded_file):
    msg = email.message_from_bytes(
        uploaded_file.getvalue(),
        policy=policy.default
    )

    subject = str(msg.get("subject", ""))
    body_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body_parts.append(part.get_content())
                except Exception:
                    continue
    else:
        try:
            if msg.get_content_type() == "text/plain":
                body_parts.append(msg.get_content())
        except Exception:
            pass

    body = "\n".join(body_parts)
    return f"Subject: {subject}\n\n{body}".strip()


def show_prediction(message, model, vectorizer):
    features = vectorizer.transform([message])
    prediction = int(model.predict(features)[0])

    probabilities = model.predict_proba(features)[0]
    classes = list(model.classes_)

    ham_probability = float(probabilities[classes.index(0)]) * 100
    spam_probability = float(probabilities[classes.index(1)]) * 100

    st.divider()
    st.subheader("📊 Analysis Result")

    if prediction == 1:
        st.error("🚨 SPAM MESSAGE")
        st.write("The model classified this message as spam.")
    else:
        st.success("✅ HAM — NOT SPAM")
        st.write("The model classified this message as not spam.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""<div class="metric-card">
            <p style="color:#86EFAC;">🟢 HAM / NOT SPAM</p>
            <h2 style="color:#86EFAC;">{ham_probability:.2f}%</h2>
            </div>""",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""<div class="metric-card">
            <p style="color:#FDA4AF;">🔴 SPAM</p>
            <h2 style="color:#FDA4AF;">{spam_probability:.2f}%</h2>
            </div>""",
            unsafe_allow_html=True
        )

    st.progress(
        spam_probability / 100,
        text=f"Estimated spam probability: {spam_probability:.2f}%"
    )

    st.caption(
        "These are model-estimated probabilities, not guarantees. "
        "This model was trained on an SMS dataset, so performance on "
        "real email may differ."
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📧 Email Spam Classifier")
st.markdown(
    '<p class="small-note">Machine learning powered message analysis</p>',
    unsafe_allow_html=True
)

try:
    model, vectorizer = load_model()
except Exception as error:
    st.error(f"Could not load model files: {error}")
    st.info("Check that both trained model files exist in the models folder.")
    st.stop()


# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------

st.header("🔍 Message Analyzer")

input_mode = st.radio(
    "Choose input method",
    ["Type or paste a message", "Upload an .eml file"],
    horizontal=True
)

message = ""

if input_mode == "Type or paste a message":
    message = st.text_area(
        "Enter message",
        placeholder="Paste your message here...",
        height=180,
        key="message_input"
    )

else:
    uploaded_file = st.file_uploader(
        "Upload an email file",
        type=["eml"],
        help="Upload a saved .eml file. This does not connect directly to Gmail or Outlook."
    )

    if uploaded_file is not None:
        try:
            message = extract_eml_text(uploaded_file)
            st.text_area(
                "Extracted email content",
                value=message,
                height=180,
                disabled=True
            )
        except Exception as error:
            st.error(f"Could not read this email file: {error}")

col1, col2 = st.columns(2)

with col1:
    analyze = st.button(
        "🔍 Analyze Message",
        use_container_width=True
    )

with col2:
    clear = st.button(
        "🧹 Clear Message",
        use_container_width=True
    )

if clear:
    st.rerun()

if analyze:
    if not message.strip():
        st.warning("Please enter a message or upload a valid .eml file.")
    else:
        try:
            show_prediction(message, model, vectorizer)
        except Exception as error:
            st.error(f"Analysis failed: {error}")


# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

st.divider()
st.header("📈 Model Performance")

summary_path = MODEL_DIR / "evaluation_summary.json"
metrics_path = MODEL_DIR / "model_metrics.csv"

if summary_path.exists():
    with open(summary_path, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    st.caption(f"Selected model: {metrics['selected_model']}")

    metric_columns = st.columns(4)

    metric_items = [
        ("Accuracy", metrics["accuracy"]),
        ("Precision", metrics["precision"]),
        ("Recall", metrics["recall"]),
        ("F1 Score", metrics["f1_score"])
    ]

    for column, (label, value) in zip(metric_columns, metric_items):
        with column:
            st.metric(label, f"{value * 100:.2f}%")

    st.metric(
        "False-positive rate",
        f"{metrics['false_positive_rate'] * 100:.2f}%"
    )

    count_columns = st.columns(4)
    count_items = [
        ("True Negative", metrics["true_negative"]),
        ("False Positive", metrics["false_positive"]),
        ("False Negative", metrics["false_negative"]),
        ("True Positive", metrics["true_positive"])
    ]

    for column, (label, value) in zip(count_columns, count_items):
        with column:
            st.metric(label, value)

else:
    st.info("Evaluation report not found. Run python train_model.py first.")


# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------

st.subheader("Confusion Matrix")

confusion_image = MODEL_DIR / "confusion_matrix.png"

if confusion_image.exists():
    st.image(
        str(confusion_image),
        caption="Held-out test-set confusion matrix",
        use_container_width=True
    )
else:
    st.info("Confusion matrix image not found. Retrain the model.")


# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

st.subheader("⚖️ Machine Learning Model Comparison")

comparison_image = MODEL_DIR / "model_comparison.png"

if comparison_image.exists():
    st.image(
        str(comparison_image),
        caption="Accuracy, precision, recall and F1 score comparison",
        use_container_width=True
    )

if metrics_path.exists():
    comparison_df = pd.read_csv(metrics_path)

    display_columns = [
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "False Positive Rate"
    ]

    if all(column in comparison_df.columns for column in display_columns):
        st.dataframe(
            comparison_df[display_columns].style.format({
                "Accuracy": "{:.2%}",
                "Precision": "{:.2%}",
                "Recall": "{:.2%}",
                "F1 Score": "{:.2%}",
                "False Positive Rate": "{:.2%}"
            }),
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# SPAM KEYWORD VISUALIZATION
# --------------------------------------------------

st.divider()
st.header("🚩 Spam-Indicating Keywords")

keyword_image = MODEL_DIR / "spam_keywords.png"
keyword_csv = MODEL_DIR / "spam_keywords.csv"

if keyword_image.exists():
    st.image(
        str(keyword_image),
        caption="Terms with higher mean TF-IDF scores in spam training messages",
        use_container_width=True
    )

if keyword_csv.exists():
    keywords = pd.read_csv(keyword_csv)

    if "keyword" in keywords.columns:
        st.subheader("Top Spam-Associated Terms")
        st.dataframe(
            keywords.head(15),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("Keyword report not found. Run python train_model.py first.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<p class="small-note">'
    'Built with Python, Streamlit, Pandas, NLTK and Scikit-learn. '
    'Charts use Matplotlib and Seaborn. '
    'This project analyzes message text and uploaded .eml files; '
    'it does not directly connect to email provider accounts.'
    '</p>',
    unsafe_allow_html=True
)