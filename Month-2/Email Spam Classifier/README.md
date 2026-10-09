
# 📧 Email Spam Classifier

A machine learning application that classifies text messages as Spam or Ham (Not Spam) and displays estimated probabilities for both classes.

## 🚀 Features

- Spam and Ham message classification
- Spam and Ham percentage estimates
- Machine learning using a calibrated Support Vector Machine (SVM)
- Text processing using TF-IDF
- Simple, professional Streamlit interface
- Real-time message prediction

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- Scikit-learn
- TF-IDF Vectorizer
- Support Vector Machine (SVM)

## 📂 Project Structure

    Email Spam Classifier/
    ├── app.py
    ├── train_model.py
    ├── requirements.txt
    ├── README.md
    ├── data/
    │   └── SMSSpamCollection
    └── models/
        ├── spam_model.pkl
        └── tfidf_vectorizer.pkl

## ⚙️ How It Works

1. Load the SMS Spam Collection dataset.
2. Convert message text into numerical features using TF-IDF.
3. Train a calibrated SVM classifier.
4. Evaluate the model using accuracy, precision, recall and F1 score.
5. Enter a message in the web application.
6. Display the predicted class and estimated Spam/Ham probabilities.

## ▶️ How to Run

### 1. Install dependencies

    pip install -r requirements.txt

### 2. Train the model

    python train_model.py

### 3. Start the application

    python -m streamlit run app.py

## 📊 Model Performance

The initial SVM model achieved 98.39% accuracy on the test dataset. Performance may differ after probability calibration and retraining.

## ⚠️ Dataset Note

This project uses the SMS Spam Collection dataset. It can classify entered text, but it does not connect to or scan an actual email inbox.

The displayed percentages are model-estimated probabilities, not guarantees that a message is safe or spam.

## 👩‍💻 Project Purpose

This project demonstrates text preprocessing, machine learning classification, model evaluation and deployment of a simple interactive application.