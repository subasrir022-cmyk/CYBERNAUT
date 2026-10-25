# PhishShift: Message Risk Scanner

## 1. Project Overview

PhishShift is a Python and Streamlit application that analyses message text, predicts whether a message is spam-like or ham-like, and highlights potentially suspicious language patterns.

The application combines a rule-based baseline, machine-learning models, message-risk cues, and evaluation visualisations.

**Important limitation:** Spam detection is not the same as phishing detection. The current supervised models use ham/spam SMS labels. Their predictions do not prove that a message is phishing or safe.

## 2. Project Objectives

- Classify message text using machine learning.
- Compare a rule-based baseline with two machine-learning models.
- Highlight suspicious cues such as links, urgency, account pressure, and requests for action.
- Report evaluation metrics and confusion matrices.
- Encourage safe handling of suspicious messages.
- Document limitations and areas requiring further validation.

## 3. Technologies Used

- Python
- Streamlit
- pandas and NumPy
- scikit-learn
- joblib
- Matplotlib
- Regular expressions
- pytest

## 4. Models Evaluated

Three approaches are compared:

1. Rule-based baseline
2. Multinomial Naive Bayes using TF-IDF features
3. Logistic Regression using TF-IDF features

Logistic Regression achieved the highest F1-score in the current reported test results. This result applies only to the evaluation dataset and split described below.

## 5. Dataset and Sources

The processed SMS Spam Collection CSV contains 5,169 rows before the evaluation script's additional exact-message deduplication. It contains 4,516 ham-labelled rows and 653 spam-labelled rows at that stage.

The evaluation script removes 11 additional duplicate message texts, leaving 5,158 messages for the reported random train/test evaluation. The class counts above are the counts before this additional deduplication; they should not be interpreted as the final evaluation split's class counts.

### UCI SMS Spam Collection

- Source: https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- Citation: Tiago Almeida and JosÃ© Hidalgo, SMS Spam Collection, UCI Machine Learning Repository.
- DOI: https://doi.org/10.24432/C5CC84
- Label meaning: ham = legitimate message in the source dataset; spam = spam message in the source dataset.

The dataset's applicable licence and redistribution terms must be verified against the original source before redistribution.

### NCSU SMS Phishing Research Dataset

- Source repository: https://github.com/wspr-ncsu/sms-phishing

The local research files include message and campaign data. Most local message-to-campaign mappings have not been independently verified, and extracted records with unknown labels must not be treated as verified benign or phishing examples.

The dataset's licence and data-use terms must be checked before redistributing its files.

**Data availability:** Raw and processed dataset files are not included in this GitHub upload. Obtain data from its original source and check the relevant terms before use. The dataset source manifest is available at docs/data_manifest.csv. Dataset licence and redistribution terms must be verified before sharing the data.

## 6. Evaluation Results

The following results are from the current stratified random holdout evaluation of ham/spam SMS classification.

| Model | Accuracy | Precision | Recall | F1-score | False Positive Rate |
|---|---:|---:|---:|---:|---:|
| Rules baseline | 89.53% | 91.67% | 17.19% | 28.95% | 0.22% |
| Multinomial Naive Bayes | 96.32% | 100.00% | 70.31% | 82.57% | 0.00% |
| Logistic Regression | 97.87% | 90.77% | 92.19% | 91.47% | 1.33% |

These metrics describe the current test split only. They do not guarantee performance on new messages, and they are not verified phishing-detection metrics.

A random split can place similar messages in both training and testing data. Campaign-separated testing and independent evaluation on unseen phishing and legitimate messages remain outstanding.

## 7. Results and Visualisations

The `results/` directory contains evaluation outputs, including:

- `model_metrics.csv` - comparison of model metrics
- `evaluation_summary.json` - dataset and evaluation summary
- `confusion_matrices.json` - confusion matrix values
- `confusion_matrix.png` - confusion matrix visualisation
- `model_comparison.png` - model comparison chart
- `spam_keywords.png` - spam keyword visualisation
- `spam_keyword_summary.csv` - keyword summary
- `campaign_matching_summary.csv` - campaign matching summary
- `hostname_extraction_summary.csv` - hostname extraction summary
- `test_set_predictions.csv` - individual test-set predictions
- `full_test_evaluation.json` - full test-set evaluation summary
- `error_analysis_summary.json` - summary of classification errors
- `pytest_output.txt` - saved automated test output

## 8. Installation and Setup

### Prerequisites

- Python installed on your computer
- Git, if cloning the repository
- The required dataset files, obtained separately from their original sources and placed in the expected local paths
- The trained model files under `models/`

### Install dependencies

Open a terminal in the project directory and run:

```bash
python -m pip install -r requirements.txt
```

### Run the application

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL in the terminal. Open that URL in your browser.

The application expects a compatible trained model file under `models/`. If model files or required local datasets are missing, complete the relevant setup before running the corresponding scripts.

## 9. Safe Usage

- Do not click suspicious links found in messages.
- Never submit passwords, one-time passwords (OTPs), PINs, or banking details.
- Verify unexpected requests through an official app, website, or trusted contact method.
- A low-risk result does not prove that a message is legitimate.
- The scanner does not open or fetch suspicious URLs.
- The heuristic risk indicator is not a calibrated probability.
- Treat uncertain results as requiring further review.

## 10. Testing and Limitations

The current project includes automated tests and saved test output. The existing test pass does not establish that every assignment acceptance criterion has been met.

Remaining work includes:

- Verify dataset licence and redistribution terms.
- Validate raw-data integrity against original downloads where possible.
- Verify near-duplicate removal and campaign-separated evaluation.
- Confirm message-to-campaign mappings and phishing-specific labels.
- Test against independent, unseen phishing and legitimate messages.
- Review URL defanging and sanitisation behaviour.
- Expand acceptance and robustness tests, including app-level behaviour.
- Preserve evidence for the final demonstration and report.

## 11. Project Status

The Streamlit interface, initial model comparison, evaluation outputs, and basic automated tests are available.
The project should not yet be described as a fully validated phishing detector. Phishing-specific validation, campaign-separated testing, dataset-permission checks, and outstanding acceptance evidence must be completed before making that claim.
