# PhishShift Threat Model

## Assets
- User-pasted message text and any private content in it.
- Local model files, source code, datasets, and evaluation results.
- Trustworthiness of the scanner's output.

## Trust boundaries
- Pasted text is untrusted input.
- Model prediction and regex cues are screening signals, not ground truth.
- Local project files are trusted only if obtained from expected project sources.

## Threats and mitigations
1. Malicious URL in a message: do not click, resolve, or fetch it; inspect text only.
2. Social-engineering language: display cues and recommend independent verification.
3. False negative: a ham-like prediction may still be malicious; never present it as guaranteed safe.
4. False positive: legitimate messages can be flagged; show the result as a model estimate.
5. Uncertain or unmapped model output: route to manual review when abstention is implemented.
6. Dataset label mismatch: SMS spam labels are not phishing labels; describe this limitation.
7. Data leakage: exact duplicates are removed, but near-duplicate and campaign-separated evaluation remain unverified.
8. Privacy exposure: scan history is session-only; avoid submitting passwords, OTPs, PINs, or private data.
9. Dependency or model tampering: install dependencies from the project's requirements and use trusted model artifacts.

## Residual risks
- Model performance may not generalize to modern phishing campaigns.
- Campaign-level independence has not been demonstrated.
- Heuristic cues can miss subtle attacks or flag legitimate messages.
- A risk index is not a calibrated phishing probability.
