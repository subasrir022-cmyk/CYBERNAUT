from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
app_path = root / "app.py"
source = app_path.read_text(encoding="utf-8")

old_prediction = '''            prediction = model.predict([message])[0]
            model_label, explanation = normalize_prediction(prediction)
            cues = detect_cues(message)
            risk, score = get_risk_level(cues)
'''

new_prediction = '''            prediction = model.predict([message])[0]
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
'''

old_display = '''                st.write(explanation)
                st.caption(f"Model file: {model_name}")
'''

new_display = '''                st.write(explanation)
                if confidence is not None:
                    st.caption(
                        f"Model confidence: {confidence:.1%}. "
                        "This is not a calibrated phishing probability."
                    )
                else:
                    st.caption("Model confidence unavailable; manual review recommended.")
                st.caption(f"Model file: {model_name}")
'''

old_action = '''            if risk in {"HIGH", "ELEVATED"} or model_label == "SPAM-LIKE":
'''

new_action = '''            if (
                risk in {"HIGH", "ELEVATED"}
                or model_label in {"SPAM-LIKE", "NEEDS REVIEW"}
            ):
'''

if not app_path.exists():
    raise FileNotFoundError("app.py not found.")

if "Model confidence: " in source:
    raise SystemExit("Confidence feature appears to exist already. No changes made.")

for name, snippet in [
    ("prediction", old_prediction),
    ("display", old_display),
    ("recommended action", old_action),
]:
    count = source.count(snippet)
    if count != 1:
        raise SystemExit(
            f"Expected one matching {name} section, found {count}. No changes made."
        )

backup = root / "app.py.before_abstention.bak"
if not backup.exists():
    shutil.copy2(app_path, backup)

updated = source.replace(old_prediction, new_prediction, 1)
updated = updated.replace(old_display, new_display, 1)
updated = updated.replace(old_action, new_action, 1)

compile(updated, str(app_path), "exec")
app_path.write_text(updated, encoding="utf-8")

print("Success: confidence-based manual review added.")
print("Backup: app.py.before_abstention.bak")
print("Threshold: 65% model confidence.")
print("Reminder: confidence is not a calibrated phishing probability.")
