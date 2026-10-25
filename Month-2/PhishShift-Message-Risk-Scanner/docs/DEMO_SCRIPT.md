# PhishShift Demo Script (3–5 minutes)

1. **Introduction (30 sec):** Explain that PhishShift is an educational message-risk screening tool, not a guarantee of safety.
2. **Dashboard (30 sec):** Show the loaded model status, session counters, and message input.
3. **Suspicious simulation (60 sec):** Select the simulated account-restriction message. Analyse it. Point out the model label, warning cues, and heuristic signal index. Do not open the URL.
4. **Ordinary simulation (45 sec):** Select the ordinary library-meeting message and analyse it. Explain that a ham-like result does not prove safety.
5. **Evaluation (45 sec):** Show `results/model_metrics.csv` and `results/confusion_matrix.png`. Explain that metrics come from a random ham/spam split, not a campaign-separated phishing benchmark.
6. **Limitations and safety (30 sec):** Mention potential false positives/negatives, unverified campaign mapping, and the need for independent sender verification.
7. **Close (10 sec):** Summarise that the tool supports review and awareness; it does not replace security controls.
