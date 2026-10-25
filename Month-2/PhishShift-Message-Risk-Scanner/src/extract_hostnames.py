
import ast
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw" / "phishing_campaigns.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "campaign_hostnames.csv"


def get_urls(value):
    if pd.isna(value):
        return []

    value = str(value).strip()

    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass

    return [value] if value else []


def extract_hostname(value):
    text = str(value).strip()

    # Extract the destination from Markdown links.
    markdown = re.search(r"\]\(([^)]+)\)", text)
    if markdown:
        text = markdown.group(1)
    elif text.startswith("[") and "](" in text:
        text = text.split("](", 1)[0].lstrip("[")

    # Normalize escaped URL characters and Unicode text.
    text = text.replace("\\", "")
    text = unicodedata.normalize("NFKC", text).strip()

    # Support URLs with or without a scheme.
    text = re.sub(r"^https?://", "", text, flags=re.IGNORECASE)
    text = text.lstrip("/")

    # Remove query strings and fragments.
    text = text.split("?", 1)[0].split("#", 1)[0]

    if not text:
        return None

    parsed = urlsplit("//" + text)
    hostname = parsed.hostname

    if not hostname:
        return None

    # Trim leading/trailing dots, but do not silently repair internal dots.
    hostname = hostname.lower().strip(".")

    try:
        hostname = hostname.encode("idna").decode("ascii")
    except (UnicodeError, ValueError):
        return None

    # Validate hostname structure.
    if "." not in hostname:
        return None

    if not re.fullmatch(r"[a-z0-9.-]+", hostname):
        return None

    if ".." in hostname:
        return None

    if any(not label for label in hostname.split(".")):
        return None

    return hostname


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    campaigns = pd.read_csv(INPUT_FILE)

    if not {"campaignID", "urls"}.issubset(campaigns.columns):
        raise ValueError("CSV must contain campaignID and urls columns.")

    rows = []

    for _, row in campaigns.iterrows():
        for url in get_urls(row["urls"]):
            hostname = extract_hostname(url)

            if hostname:
                rows.append({
                    "campaignID": row["campaignID"],
                    "hostname": hostname,
                })

    output = pd.DataFrame(
        rows, columns=["campaignID", "hostname"]
    ).drop_duplicates()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    all_ids = set(campaigns["campaignID"].astype(str))
    found_ids = set(output["campaignID"].astype(str))
    missing_ids = sorted(all_ids - found_ids)

    print("Hostname extraction completed.")
    print("Original campaign rows:", len(campaigns))
    print("Extracted campaign-hostname pairs:", len(output))
    print("Campaigns represented:", output["campaignID"].nunique())
    print("Unique hostnames:", output["hostname"].nunique())
    print("Campaigns without extracted hostnames:", len(missing_ids))

    if missing_ids:
        print("Missing campaign IDs:", ", ".join(missing_ids))

    print("\nTop 15 hostnames:")
    if not output.empty:
        print(output["hostname"].value_counts().head(15).to_string())

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
