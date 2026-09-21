import pandas as pd
from textblob import TextBlob


def analyze_sentiment(review):

    analysis = TextBlob(review)

    polarity = analysis.sentiment.polarity

    if polarity > 0:
        sentiment = "Positive"

    elif polarity < 0:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return sentiment, polarity


# Read review data
df = pd.read_csv("data/reviews.csv")


# Analyze every review
sentiments = []
polarities = []

for review in df["review"]:

    sentiment, polarity = analyze_sentiment(review)

    sentiments.append(sentiment)
    polarities.append(polarity)


# Add results to dataframe
df["sentiment"] = sentiments
df["polarity"] = polarities


# Display results
print("\n======================================")
print("PRODUCT SENTIMENT ANALYZER")
print("======================================")

print("\nTotal Reviews:", len(df))

print("\nReviews with Sentiment:")
print(
    df[
        [
            "product",
            "review",
            "rating",
            "sentiment",
            "polarity"
        ]
    ]
)


# Sentiment counts
sentiment_counts = df["sentiment"].value_counts()


print("\n======================================")
print("SENTIMENT SUMMARY")
print("======================================")

print(sentiment_counts)


# Average rating
average_rating = df["rating"].mean()

print(
    "\nAverage Rating:",
    round(average_rating, 2)
)


# Save analyzed data
df.to_csv(
    "data/analyzed_reviews.csv",
    index=False
)


print(
    "\nAnalyzed reviews saved successfully!"
)