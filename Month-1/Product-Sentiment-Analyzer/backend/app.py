from flask import Flask, jsonify, send_from_directory
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter
import re
import os

app = Flask(__name__)

# ======================================
# PROJECT PATH
# ======================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================
# LOAD ENVIRONMENT VARIABLES
# ======================================

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("ERROR: MONGO_URI not found in .env")
    raise SystemExit

# ======================================
# MONGODB CONNECTION
# ======================================

client = MongoClient(MONGO_URI)

db = client["product_sentiment_db"]
collection = db["reviews"]


# ======================================
# HOME PAGE
# ======================================

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR / "frontend",
        "index.html"
    )


# ======================================
# REVIEWS API
# ======================================

@app.route("/api/reviews")
def get_reviews():

    reviews = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    return jsonify(reviews)


# ======================================
# WORD FREQUENCY API
# ======================================

@app.route("/api/word-frequency")
def get_word_frequency():

    reviews = list(
        collection.find(
            {},
            {
                "_id": 0,
                "review": 1
            }
        )
    )

    all_reviews = " ".join(
        review["review"]
        for review in reviews
        if "review" in review
    )

    all_reviews = all_reviews.lower()

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        all_reviews
    )

    stop_words = {
        "the",
        "and",
        "for",
        "are",
        "this",
        "that",
        "with",
        "very",
        "these",
        "they",
        "from",
        "product",
        "really",
        "after",
        "working",
        "worth",
        "money"
    }

    filtered_words = [
        word
        for word in words
        if word not in stop_words
    ]

    word_counts = Counter(filtered_words)

    top_words = [
        {
            "word": word,
            "count": count
        }
        for word, count
        in word_counts.most_common(10)
    ]

    return jsonify(top_words)


# ======================================
# SENTIMENT TREND API
# ======================================

@app.route("/api/sentiment-trend")
def get_sentiment_trend():

    reviews = list(
        collection.find(
            {},
            {
                "_id": 0,
                "date": 1,
                "sentiment": 1
            }
        )
    )

    trend_data = {}

    for review in reviews:

        date = review.get("date")
        sentiment = review.get("sentiment")

        if not date:
            continue

        if date not in trend_data:

            trend_data[date] = {
                "Positive": 0,
                "Negative": 0,
                "Neutral": 0
            }

        if sentiment in trend_data[date]:

            trend_data[date][sentiment] += 1


    dates = sorted(trend_data.keys())

    result = []

    for date in dates:

        result.append({
            "date": date,
            "Positive": trend_data[date]["Positive"],
            "Negative": trend_data[date]["Negative"],
            "Neutral": trend_data[date]["Neutral"]
        })

    return jsonify(result)


# ======================================
# RUN FLASK
# ======================================

if __name__ == "__main__":

    app.run(debug=True)