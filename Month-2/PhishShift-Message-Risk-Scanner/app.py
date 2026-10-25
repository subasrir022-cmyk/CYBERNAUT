
import re
import joblib
import streamlit as st
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

st.set_page_config(
    page_title="PhishShift | Cyber Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background:
      radial-gradient(ellipse at 10% 0%, #10264a 0%, transparent 38%),
      radial-gradient(ellipse at 100% 40%, #071b35 0%, transparent 35%),
      #050914;
    color: #edf8ff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091426, #050914);
    border-right: 1px solid rgba(0,229,255,.2);
}
[data-testid="stSidebar"] * { color: #d9edff; }
h1,h2,h3 { color: #f0fbff !important; }
.hero {
    padding: 28px;
    border: 1px solid rgba(0,229,255,.3);
    border-radius: 20px;
    background: linear-gradient(120deg, #0b1f3a, #070f20);
    box-shadow: 0 0 30px rgba(0,180,255,.08);
    margin-bottom: 22px;
}
.eyebrow {
    color: #00e5ff;
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: 700;
}
.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(26px, 3vw, 42px);
    font-weight: 800;
    color: white;
    margin: 8px 0;
}
.hero-title span {
    color: #00e5ff;
    text-shadow: 0 0 18px rgba(0,229,255,.45);
}
.hero-sub { color: #9db7d5; font-size: 14px; line-height: 1.8; }
.metric-card {
    background: linear-gradient(145deg, #0e1d33, #091222);
    border: 1px solid rgba(57,133,255,.32);
    border-radius: 14px;
    padding: 18px;
    min-height: 100px;
}
.metric-label { color: #8fa8c7; font-size: 11px; letter-spacing: 1.5px; }
.metric-value { color: #f3fbff; font-size: 22px; font-weight: 700; margin-top: 10px; }
.neon { color: #00e5ff; text-shadow: 0 0 12px rgba(0,229,255,.35); }
.panel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    letter-spacing: 1px;
    color: #00e5ff;
    margin-bottom: 12px;
}
.stTextArea textarea {
    background: #071120 !important;
    color: #e8f7ff !important;
    border: 1px solid #1d496b !important;
    border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(100deg, #00d9ff, #3985ff);
    color: #04101f !important;
    border: none;
    border-radius: 10px;
    font-weight: 800;
    min-height: 44px;
}
.stButton > button:hover {
    box-shadow: 0 0 22px rgba(0,229,255,.32);
}
hr { border-color: rgba(0,229,255,.15); }
.small-muted { color: #9db7d5; font-size: 12px; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)


# Load a saved model. Prefer the Logistic Regression artifact.
@st.cache_resource
def load_model():
    if not MODEL_DIR.exists():
        return None, "Models folder not found"

    files = list(MODEL_DIR.glob("*.joblib"))
    files.sort(
        key=lambda p: (
            0 if "logistic_regression" in p.name.lower() else 1,
            p.name.lower()
        )
    )

    for path in files:
        try:
            candidate = joblib.load(path)
            if hasattr(candidate, "predict"):
                return candidate, path.name
        except Exception:
            continue

    return None, "No compatible .joblib model found"


model, model_name = load_model()


def normalize_prediction(prediction):
    # Assumes training labels: spam=1, ham=0.
    label = str(prediction).strip().lower()

    if label in {"spam", "phishing", "malicious", "fraud", "1", "1.0"}:
        return "SPAM-LIKE", "Model prediction: spam-like message."

    if label in {"ham", "legitimate", "benign", "safe", "0", "0.0"}:
        return "HAM-LIKE", (
            "Model prediction: ham-like message. This does not guarantee safety."
        )

    return "UNMAPPED OUTPUT", (
        f"The model returned '{prediction}'. Label meaning needs verification."
    )


def detect_cues(message):
    patterns = [
        (r"https?://\S+|www\.\S+", "Link detected",
         "Unexpected links can lead to fake login or payment pages."),
        (r"\b(verify|verification|confirm|update)\b", "Verification request",
         "The message requests verification or an update."),
        (r"\b(suspended|blocked|restricted|locked|deactivated)\b",
         "Account pressure", "Account restriction language can create fear."),
        (r"\b(urgent|immediately|act now|limited time|right now)\b",
         "Urgency language", "Pressure to act quickly can discourage careful checking."),
        (r"\b(password|otp|pin|bank details|card details)\b",
         "Sensitive information mentioned", "Never share passwords, PINs or OTPs."),
        (r"\b(prize|winner|claim|free reward|cash bonus|lottery)\b",
         "Prize or reward language", "Unexpected rewards can be used to lure recipients."),
        (r"\b(click here|tap here|login now|sign in now)\b",
         "Action request", "Verify requests independently before taking action.")
    ]

    return [
        {"title": title, "explanation": explanation}
        for pattern, title, explanation in patterns
        if re.search(pattern, message, re.IGNORECASE)
    ]


def get_risk_level(cues):
    # Heuristic indicator, NOT a probability of phishing.
    count = len(cues)
    if count >= 4:
        return "HIGH", 85
    if count >= 2:
        return "ELEVATED", 60
    if count == 1:
        return "CAUTION", 35
    return "LOW SIGNAL", 10


if "scan_history" not in st.session_state:
    st.session_state.scan_history = []


# Sidebar
with st.sidebar:
    st.markdown("<div class='eyebrow'>PHISHSHIFT // CONSOLE</div>", unsafe_allow_html=True)
    st.markdown("## 🛡️ Cyber Console")
    st.caption("MESSAGE INTELLIGENCE SYSTEM")
    st.divider()
    st.markdown("**SYSTEM STATUS**")

    if model is not None:
        st.success("Predictive model loaded")
    else:
        st.error("Predictive model unavailable")
        st.caption(model_name)

    st.markdown("**ACTIVE MODULES**")
    st.write("◈ Message classification")
    st.write("◈ Warning cue analysis")
    st.write("◈ Local text processing")
    st.divider()
    st.caption("Never share passwords, OTPs, PINs or banking information.")

    if st.button("Clear Scan History", use_container_width=True):
        st.session_state.scan_history = []
        st.rerun()


# Main header
st.markdown("""
<div class="hero">
  <div class="eyebrow">CYBER DEFENCE // MESSAGE INTELLIGENCE</div>
  <div class="hero-title">PHISH<span>SHIFT</span></div>
  <div style="font-size:15px;color:#dcefff;font-weight:600;">
    MESSAGE RISK SCANNER
  </div>
  <div class="hero-sub">
    Inspect suspicious messages, review model predictions and identify warning cues.<br>
    Stay alert. Verify independently. Never trust a message blindly.
  </div>
</div>
""", unsafe_allow_html=True)


# Dashboard metrics
history = st.session_state.scan_history
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>SESSION SCANS</div>"
        f"<div class='metric-value neon'>{len(history)}</div></div>",
        unsafe_allow_html=True
    )

with m2:
    high_flags = sum(1 for item in history if item["risk"] == "HIGH")
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>HIGH SIGNAL FLAGS</div>"
        f"<div class='metric-value'>{high_flags}</div></div>",
        unsafe_allow_html=True
    )

with m3:
    status = "ONLINE" if model is not None else "OFFLINE"
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>MODEL STATUS</div>"
        f"<div class='metric-value neon'>{status}</div></div>",
        unsafe_allow_html=True
    )

st.write("")

left, right = st.columns([1.25, 0.75], gap="large")

with left:
    st.markdown("<div class='panel-title'>01 // MESSAGE INPUT</div>", unsafe_allow_html=True)

    sample = st.selectbox(
        "Try a sample",
        [
            "Custom message",
            "Suspicious account message (simulation)",
            "Prize message (simulation)",
            "Ordinary message (simulation)"
        ]
    )

    samples = {
        "Suspicious account message (simulation)":
            "URGENT: Your account is restricted. Verify your details immediately at https://example.invalid/login",
        "Prize message (simulation)":
            "Congratulations! You are a winner. Click here to claim your free reward now.",
        "Ordinary message (simulation)":
            "Hi, I will meet you at the library after class. See you at 4 PM."
    }

    message = st.text_area(
        "Message content",
        value=samples.get(sample, ""),
        height=190,
        placeholder="Paste a message here. Do not open links inside it.",
        max_chars=10000
    )

    scan_clicked = st.button("⌁ ANALYSE MESSAGE", use_container_width=True)

with right:
    st.markdown("""
    <div class="panel">
      <div class="panel-title">02 // SCAN GUIDELINES</div>
      <p>01 — Paste the complete message</p>
      <p>02 — Review model output and warning cues</p>
      <p>03 — Verify the sender through a trusted channel</p>
      <hr>
      <div class="small-muted">
      This scanner does not open links or verify websites. Treat results as screening signals.
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("What can this scanner detect?"):
        st.write(
            "• Spam-like message patterns\n"
            "• Urgency and account-pressure wording\n"
            "• Mentions of sensitive information\n"
            "• Links and reward-related wording"
        )
        st.caption("Legitimate messages may also contain these patterns.")


# Analysis
if scan_clicked:
    if not message.strip():
        st.warning("Enter a message before starting the scan.")

    elif model is None:
        st.error("Model unavailable. Check the models folder.")
        st.caption(model_name)

    else:
        try:
            prediction = model.predict([message])[0]
            model_label, explanation = normalize_prediction(prediction)

            confidence = None
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba([message])[0]
                confidence = float(max(probabilities))

            if confidence is None or confidence < 0.65:
                model_label = "NEEDS REVIEW"
                explanation = (
                    "The model confidence is low or unavailable. "
                    "Please review this message manually."
                )

            cues = detect_cues(message)
            risk, score = get_risk_level(cues)

            st.session_state.scan_history.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "risk": risk,
                "prediction": model_label,
                "cues": len(cues),
                "message": message[:120]
            })
            st.session_state.scan_history = st.session_state.scan_history[:10]

            st.markdown("---")
            st.markdown("<div class='eyebrow'>03 // ANALYSIS REPORT</div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("<div class='panel-title'>MODEL CLASSIFICATION</div>", unsafe_allow_html=True)

                if model_label == "SPAM-LIKE":
                    st.error("⚠️ SPAM-LIKE PREDICTION")
                elif model_label == "HAM-LIKE":
                    st.success("✓ HAM-LIKE PREDICTION")
                else:
                    st.warning("MODEL OUTPUT NEEDS REVIEW")

                st.write(explanation)
                if confidence is not None:
                    st.caption(
                        f"Model confidence: {confidence:.1%}. "
                        "This is not a calibrated phishing probability."
                    )
                else:
                    st.caption("Model confidence unavailable; manual review recommended.")
                st.caption(f"Model file: {model_name}")

            with col_b:
                st.markdown("<div class='panel-title'>WARNING SIGNAL INDEX</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value neon'>{risk}</div>", unsafe_allow_html=True)
                st.progress(score / 100)
                st.caption(
                    f"Heuristic indicator: {score}/100. "
                    "Based on warning-pattern count, not phishing probability."
                )

            st.markdown("### ◈ Warning Cue Breakdown")

            if cues:
                for cue in cues:
                    with st.container(border=True):
                        st.markdown(f"**⚡ {cue['title']}**")
                        st.write(cue["explanation"])
            else:
                st.info("No listed warning patterns detected. This does not mean the message is safe.")

            st.markdown("### ◈ Recommended Action")

            if (
                risk in {"HIGH", "ELEVATED"}
                or model_label in {"SPAM-LIKE", "NEEDS REVIEW"}
            ):
                st.warning(
                    "Do not click links or share sensitive information. "
                    "Contact the organisation through its official app or trusted number."
                )
            else:
                st.info("Verify unexpected requests independently before taking action.")

            st.caption(
                "Session history is temporary and is not saved to a database by this code."
            )

        except Exception as exc:
            st.error("The message could not be analysed.")
            st.caption(f"Technical detail: {exc}")


# Recent scans
st.markdown("---")
st.markdown("### ◈ Recent Scan Activity")

if not st.session_state.scan_history:
    st.caption("No scans in this session yet.")
else:
    for item in st.session_state.scan_history:
        with st.container(border=True):
            c1, c2, c3 = st.columns([0.7, 1, 2])
            c1.caption(item["time"])
            c2.write(f"**{item['risk']}**")
            c3.write(item["prediction"])
            c3.caption(f"{item['cues']} warning cue(s) · {item['message']}")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;padding:16px 0;'>"
    "<div class='eyebrow'>PHISHSHIFT // STAY CYBER AWARE</div>"
    "<div class='small-muted'>Educational screening tool · Not a guarantee of safety</div>"
    "</div>",
    unsafe_allow_html=True
)
