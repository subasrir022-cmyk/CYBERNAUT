
import pickle
import streamlit as st

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Email Spam Classifier",
    page_icon="📧",
    layout="centered"
)

# ---------------- PROFESSIONAL STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #F1F5F9;
}

.block-container {
    max-width: 700px;
    padding-top: 2.5rem;
}

h1 {
    color: #7DD3FC !important;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #A7B5CC;
    margin-bottom: 30px;
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
    height: 48px;
    font-weight: bold;
    width: 100%;
}

.result-card {
    padding: 22px 10px;
    border-radius: 14px;
    background: #111C30;
    border: 1px solid #33445F;
    text-align: center;
}

.result-number {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ---------------- LOAD TRAINED MODEL ----------------
@st.cache_resource
def load_model():
    with open("models/spam_model.pkl", "rb") as file:
        model = pickle.load(file)

    with open("models/tfidf_vectorizer.pkl", "rb") as file:
        vectorizer = pickle.load(file)

    return model, vectorizer


# ---------------- WEBSITE HEADING ----------------
st.markdown(
    "<h1>📧 Email Spam Classifier</h1>",
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Check whether your message is Spam or Ham using Machine Learning'
    '</div>',
    unsafe_allow_html=True
)


# ---------------- MESSAGE INPUT ----------------
message = st.text_area(
    "Enter your message",
    placeholder="Type or paste your email message here...",
    height=140
)

analyze = st.button("🔍 Analyze Message", use_container_width=True)


# ---------------- PREDICTION ----------------
if analyze:

    if not message.strip():
        st.warning("Please enter a message first.")

    else:
        try:
            model, vectorizer = load_model()

            # Convert message into numerical features
            message_features = vectorizer.transform([message])

            # Predict the class: 0 = Ham, 1 = Spam
            prediction = int(model.predict(message_features)[0])

            # Get estimated class probabilities
            probabilities = model.predict_proba(message_features)[0]

            # Find the correct probability for each class
            classes = list(model.classes_)
            ham_index = classes.index(0)
            spam_index = classes.index(1)

            ham_percentage = float(probabilities[ham_index]) * 100
            spam_percentage = float(probabilities[spam_index]) * 100

            st.divider()
            st.subheader("📊 Analysis Result")

            # Show the predicted result
            if prediction == 1:
                st.error("🚨 SPAM MESSAGE")
                st.write("This message has been classified as spam.")

            else:
                st.success("✅ HAM — NOT SPAM")
                st.write("This message has been classified as not spam.")

            # Show both percentages
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div style="color:#86EFAC;">
                            🟢 HAM / NOT SPAM
                        </div>
                        <div class="result-number"
                             style="color:#86EFAC;">
                            {ham_percentage:.2f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div style="color:#FDA4AF;">
                            🔴 SPAM
                        </div>
                        <div class="result-number"
                             style="color:#FDA4AF;">
                            {spam_percentage:.2f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Visual spam percentage indicator
            st.progress(
                float(spam_percentage / 100),
                text=f"Estimated Spam Likelihood: {spam_percentage:.2f}%"
            )

            st.caption(
                "Percentages are model-estimated probabilities, "
                "not guarantees. Even a message classified as Ham "
                "may be unsafe."
            )

        except FileNotFoundError:
            st.error(
                "Model files not found. Please run "
                "'python train_model.py' first."
            )

        except AttributeError:
            st.error(
                "The saved model does not support probability estimates. "
                "Please run 'python train_model.py' again, then restart "
                "this app."
            )

        except Exception as error:
            st.error(f"Something went wrong: {error}")


# ---------------- FOOTER ----------------
st.divider()

st.markdown(
    "<div style='text-align:center;color:#A7B5CC;font-size:13px;'>"
    "Email Spam Classifier | Python • Streamlit • Machine Learning"
    "</div>",
    unsafe_allow_html=True
)