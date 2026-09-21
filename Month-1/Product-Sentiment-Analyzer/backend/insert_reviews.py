import pandas as pd
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
import os

# Project base folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("ERROR: MONGO_URI not found in .env")
    raise SystemExit

# Connect to MongoDB
client = MongoClient(MONGO_URI)

db = client["product_sentiment_db"]
collection = db["reviews"]

# Read analyzed reviews
csv_file = BASE_DIR / "data" / "analyzed_reviews.csv"
df = pd.read_csv(csv_file)

# Convert date to string
df["date"] = df["date"].astype(str)

records = df.to_dict("records")

inserted = 0
updated = 0

# Insert or update reviews
for record in records:

    result = collection.update_one(
        {
            "product": record["product"],
            "review": record["review"],
            "rating": record["rating"]
        },
        {
            "$set": record
        },
        upsert=True
    )

    if result.upserted_id is not None:
        inserted += 1
    else:
        updated += 1

print("======================================")
print("MONGODB REVIEW SYNC")
print("======================================")
print("Total CSV reviews processed:", len(records))
print("New reviews inserted:", inserted)
print("Existing reviews updated:", updated)
print("Date field synced successfully!")
print("MongoDB sync completed successfully!")

client.close()