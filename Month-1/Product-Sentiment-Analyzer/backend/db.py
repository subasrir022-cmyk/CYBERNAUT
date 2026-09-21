import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("ERROR: MONGO_URI not found in .env")
    exit()

print("MongoDB URI loaded successfully!")

client = MongoClient(MONGO_URI)

client.admin.command("ping")

print("MongoDB connected successfully!")