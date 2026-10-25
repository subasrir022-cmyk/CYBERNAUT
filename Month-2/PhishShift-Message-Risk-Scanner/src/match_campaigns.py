
import re
from pathlib import Path

import pandas as pd


# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent

MESSAGES_FILE = (
    PROJECT_ROOT / "data" / "processed" / "ncsu_messages_extracted.csv"
)
CAMPAIGNS_FILE = PROJECT_ROOT / "data" / "raw" / "phishing_campaigns.csv"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "campaign_match_candidates.csv"
)


def normalize_message(text):
    """
    Normalize campaign templates and raw SMS messages
    for exploratory matching only.
    """
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()

    # Replace Markdown links with their actual URL.
    text = re.sub(
        r"\[([^\]]*)\]\((https?://[^)]+)\)",
        r"\2",
        text,
    )

    # Normalize URLs, including common escaped URL formats.
    text = re.sub(
        r"https?\\?\s*:\s*\\?/?\S+",
        " #URL ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bwww\.\S+", " #URL ", text)

    # Normalize email addresses.
    text = re.sub(
        r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b",
        " #EMAIL ",
        text,
        flags=re.IGNORECASE,
    )

    # Normalize phone-like sequences.
    text = re.sub(
        r"(?<!\w)\+?\d[\d\s().-]{6,}\d(?!\w)",
        " #PHONE ",
        text,
    )

    # Make campaign numeric placeholders comparable with message values.
    text = re.sub(r"#otp", " #NUM ", text)
    text = re.sub(r"\b\d+(?:[.,]\d+)?\b", " #NUM ", text)

    # Remove leftover Markdown punctuation and normalize spaces.
    text = re.sub(r"[\[\]()]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    if not MESSAGES_FILE.exists():
        raise FileNotFoundError(
            f"Messages file not found: {MESSAGES_FILE}"
        )

    if not CAMPAIGNS_FILE.exists():
        raise FileNotFoundError(
            f"Campaign file not found: {CAMPAIGNS_FILE}"
        )

    messages = pd.read_csv(MESSAGES_FILE)
    campaigns = pd.read_csv(CAMPAIGNS_FILE)

    required_message_cols = {"messageID", "message_text"}
    required_campaign_cols = {"campaignID", "message"}

    if not required_message_cols.issubset(messages.columns):
        raise ValueError(
            f"Messages file must contain: {sorted(required_message_cols)}"
        )

    if not required_campaign_cols.issubset(campaigns.columns):
        raise ValueError(
            f"Campaign file must contain: {sorted(required_campaign_cols)}"
        )

    # Build a lookup of normalized campaign templates.
    template_lookup = {}

    for _, row in campaigns.iterrows():
        normalized_template = normalize_message(row["message"])

        if normalized_template:
            template_lookup.setdefault(
                normalized_template, []
            ).append(row["campaignID"])

    # Compare messages with normalized campaign templates.
    normalized_messages = []
    matched_campaign_ids = []
    match_statuses = []

    for _, row in messages.iterrows():
        normalized = normalize_message(row["message_text"])
        normalized_messages.append(normalized)

        campaign_ids = template_lookup.get(normalized, [])

        if len(campaign_ids) == 1:
            matched_campaign_ids.append(str(campaign_ids[0]))
            match_statuses.append("candidate_match")
        elif len(campaign_ids) > 1:
            matched_campaign_ids.append(
                ";".join(map(str, campaign_ids))
            )
            match_statuses.append("ambiguous_match")
        else:
            matched_campaign_ids.append("")
            match_statuses.append("unmatched")

    # Preserve original extracted records and existing labels.
    output = messages.copy()
    output["normalized_message"] = normalized_messages
    output["candidate_campaign_ids"] = matched_campaign_ids
    output["match_status"] = match_statuses

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("Campaign template matching completed.")
    print(f"Messages checked: {len(output)}")
    print(f"Campaign rows checked: {len(campaigns)}")
    print(f"Unique normalized templates: {len(template_lookup)}")
    print("\nMatch status counts:")
    print(
        output["match_status"]
        .value_counts()
        .to_string()
    )
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print(
        "\nReminder: candidate matches are exploratory, "
        "not independently verified labels."
    )


if __name__ == "__main__":
    main()
